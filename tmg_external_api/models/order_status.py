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
                        and (CAST(partner.id AS VARCHAR(20)) = %(Partner_ID)s
                          OR CAST(partner.parent_id AS VARCHAR(20)) = %(Partner_ID)s
                          OR %(Partner_ID)s = ''
                          OR %(Partner_ID)s =
                                (SELECT parent_id
                                 FROM res_partner
                                 WHERE id = partner.parent_id))
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
                ship_date = ''
                if order.invoice_status == 'invoiced':
                    pickings = order.picking_ids.filtered(lambda pick: pick.state == 'done').sorted('date_done')[0]
                    ship_date = pickings.date_done
                else:
                    ship_date = order.commitment_date
                data = [

                    ('active', '=', True),
                    # ('parent_id', '=', partner_id.parent_id.id),
                    ('name', '=', order.name),
                    ('ship_date', '=', ship_date),
                    ('in_hands', '=', order.in_hands),
                    ('status', '=', orderStatus[0]),
                    ('SONumber', '=', order.name),
                    ('PONumber', '=', order.client_order_ref),
                    ('state_name', '=', orderStatus[1])
                ]
                itemList.append(data)

            return itemList

    def _get_lookup_value(self, name, category):
        cont = self.env['tmg_external_api.tmg_reference']
        val = cont.search([('category', '=', category), ('value', '=', name)])
        return val.name or 'General Hold'

    def _get_current_status(self, order):
        if order.state == 'cancel':
            return [14, 'Canceled']
        if order.invoice_status == 'invoiced':
            return [13, 'Complete']
        if order.order_holds:
            credit_found = False
            has_hold = False
            current_hold = 0
            current_desc = ''
            for hold in order.order_holds:
                has_hold = True
                desc = int(hold.promostandards_hold_description)
                hold_type = self._get_lookup_value(desc,'promostandards_order_status')
                if desc > current_hold:
                    current_hold = desc
                    current_desc = hold_type



            if has_hold:
                return [int(current_hold), current_desc]
        for prod in order.production_ids:
            if prod.state == 'progress':
                return [10, 'In Progress']
        return [2, 'Order Confirmed']