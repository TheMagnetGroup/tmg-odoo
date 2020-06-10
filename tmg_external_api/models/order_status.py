# -*- coding: utf-8 -*-
from datetime import date, datetime
from odoo import models, fields, api
import json


class order_status(models.Model):
    _name = 'tmg_external_api.order_status'


    def OrderStatus(self, PONumber, SONumber, LastUpdate, Partner_id):
            if LastUpdate == '':
                LastUpdate = '02/01/1990'
            sql = """SELECT sale.id
                        FROM sale_order as sale
                        join res_partner partner ON (partner.id = sale.partner_id)
                        where (client_order_ref = %(PONumber)s or %(PONumber)s =  '')
                        and ((CAST(partner.id as VARCHAR(20)) = %(Partner_ID)s or CAST(partner.parent_id as VARCHAR(20)) = %(Partner_ID)s) or %(Partner_ID)s = '')
                        and (sale.name = %(SONumber)s or %(SONumber)s = '')
                        and (sale.write_date >= %(LastUpdate)s);"""
            params = {
                'PONumber': PONumber,
                'SONumber': SONumber,
                'LastUpdate': LastUpdate,
                'Partner_ID': Partner_id,
            }
            self.env.cr.execute(sql, params)
            orderObj = self.env['sale.order']
            itemList = []

            for val in self.env.cr.dictfetchall():
                order_id = val['id']
                order = orderObj.browse(order_id)
                orderStatus = self._get_current_status(order)

                data = [

                    ('active', '=', True),
                    # ('parent_id', '=', partner_id.parent_id.id),
                    ('name', '=', order.name),
                    ('ship_date', '=', order.expected_date),
                    ('in_hands', '=', order.in_hands),
                    ('status', '=', orderStatus),
                    ('SONumber', '=', order.name),
                    ('PONumber', '=', order.client_order_ref)
                ]
                itemList.append(data)

            return itemList

    def _get_current_status(self, order):
        if order.state == 'cancel':
            return 'Canceled'
        if order.invoice_status == 'invoiced':
            return 'Completed'
        if order.order_holds:
            credit_found = False
            has_hold = False
            for hold in order.order_holds:
                if hold.credit_hold:
                    credit_found = True
                    return 'Credit Hold'
                has_hold = True
            if has_hold:
                return 'General Hold'
        for prod in order.production_ids:
            if prod.state == 'progress':
                return 'production'
        return 'Confirmed'