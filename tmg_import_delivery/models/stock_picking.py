# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _get_ups_service_types(self):
        return self.env['delivery.carrier']._get_ups_service_types()

    def get_fedex_service_types(self):
        return self.env['delivery.carrier'].get_fedex_service_types()

    shipping_reference_1 = fields.Char(string="Shipping Reference 1")
    shipping_reference_2 = fields.Char(string="Shipping Reference")
    carrier_id = fields.Many2one('delivery.carrier', string="Carrier")
    fedex_bill_my_account = fields.Boolean(related='carrier_id.fedex_bill_my_account', readonly=True)
    fedex_carrier_account = fields.Char(string='Fedex Carrier Account', readonly=False)
    ups_carrier_account = fields.Char(string='UPS Carrier Account', readonly=False)
    ups_service_type = fields.Selection(_get_ups_service_types, string="UPS Service Type")
    fedex_service_type = fields.Selection(get_fedex_service_types, string="Fedex Service Type")
    ups_bill_my_account = fields.Boolean(related='carrier_id.ups_bill_my_account', readonly=True)


    # @api.multi
    # @api.onchange('carrier_id')
    # def _clear_shipping(self):
    #     if self.carrier_id.fedex_bill_my_account:
    #         self.ups_service_type = False
    #         self.ups_carrier_account = False
    #     else:
    #         self.fedex_carrier_account = False
    #         self.fedex_service_type = False
    #
    #     if self.carrier_id.ups_bill_my_account:
    #         self.fedex_carrier_account = False
    #         self.fedex_service_type = False
    #     else:
    #         self.ups_service_type = False
    #         self.ups_carrier_account = False

