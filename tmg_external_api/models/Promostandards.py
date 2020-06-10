# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, datetime
import json


class promostandards(models.Model):
    _name = 'tmg_external_api.promostandards'

    name = fields.Char(string="API Name")

    debug = fields.Boolean(string="Debug Mode")



    @api.multi
    def get_partner(self, partner_id):
        if not partner_id:
            return False
        partner_obj = self.env['res.partner']
        partner = partner_obj.browse(int(partner_id))
        return partner

    @api.multi
    def get_api(self, api_name):
        api_container = self.env['tmg_external_api.promostandards']
        apiID = api_container.search([('name', '=', api_name)])
        return apiID

    @api.multi
    def check_call_cap(self, partner_id):
        partner = self.get_partner(partner_id)
        if partner.current_call_count + 1 > partner.daily_call_cap:
            return False
        else:
            return True

    @api.multi
    def _check_debug(self, partner_id, api_name):
        partner = self.get_partner(partner_id)
        api = self.get_api(api_name)
        if api.debug or partner.debug:
            return True
        else:
            return False

    @api.multi
    def log_transaction(self, partner_id, request, api_name):
        partner = self.get_partner(partner_id)
        partner.current_call_count += 1
        if self._check_debug(partner_id, api_name) :
            log_obj = self.env("tmg_external_api.api_logging")
            new_log = log_obj.create({
                'api_name': api_name,
                'partner_id': partner_id,
                'request': request,

            })
            return True

    #Test function for call cap
    # @api.multi
    # def test_button(self):
    #     test = self.OrderStatus("","","","156409"," fjfj")

    @api.multi
    def OrderStatus(self, PONumber, SONumber, LastUpdate, Partner_id, Request):
        if not self.check_call_cap(Partner_id):
            data = [('Error', '=', "Call Cap") ]
            return data


        statusObj = self.env['tmg_external_api.order_status']
        data = statusObj.OrderStatus(PONumber, SONumber,LastUpdate,Partner_id)
        self.log_transaction(Partner_id,Request,"Order Status")
        return data
    # def OrderStatus(self, PONumber, SONumber, LastUpdate, Partner_id):
    #     if LastUpdate == '':
    #         LastUpdate = '02/01/1990'
    #     sql = """SELECT sale.id
    #                 FROM sale_order as sale
    #                 join res_partner partner ON (partner.id = sale.partner_id)
    #                 where (client_order_ref = %(PONumber)s or %(PONumber)s =  '')
    #                 and (CAST(partner.id as VARCHAR(20)) = %(Partner_ID)s or %(Partner_ID)s = '')
    #                 and (sale.name = %(SONumber)s or %(SONumber)s = '')
    #                 and (sale.write_date >= %(LastUpdate)s);"""
    #     params = {
    #         'PONumber': PONumber,
    #         'SONumber': SONumber,
    #         'LastUpdate': LastUpdate,
    #         'Partner_ID': Partner_id,
    #     }
    #     self.env.cr.execute(sql, params)
    #     orderObj = self.env['sale.order']
    #     itemList = []
    #
    #     for val in self.env.cr.dictfetchall():
    #         order_id = val['id']
    #         order = orderObj.browse(order_id)
    #         orderStatus = self._get_current_status(order)
    #
    #         data = [
    #
    #             ('active', '=', True),
    #             # ('parent_id', '=', partner_id.parent_id.id),
    #             ('name', '=', order.name),
    #             ('ship_date', '=', order.expected_date),
    #             ('in_hands', '=', order.in_hands),
    #             ('status', '=', orderStatus),
    #             ('SONumber', '=', order.name)
    #         ]
    #         itemList.append(data)
    #     json_string = json.dumps(itemList)
    #     return itemList
    #
    # def _get_current_status(self, order):
    #     if order.state == 'cancel':
    #         return 'Canceled'
    #     if order.invoice_status == 'invoiced':
    #         return 'Completed'
    #     if order.order_holds:
    #         credit_found = False
    #         has_hold = False
    #         for hold in order.order_holds:
    #             if hold.credit_hold:
    #                 credit_found = True
    #                 return 'Credit Hold'
    #             has_hold = True
    #         if has_hold:
    #             return 'General Hold'
    #     return 'Confirmed'


