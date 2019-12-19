# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _get_ups_service_types(self):
        return self.env['delivery.carrier']._get_ups_service_types()

    carrier_id = fields.Many2one('delivery.carrier', string="Carrier")
    fedex_bill_my_account = fields.Boolean(related='carrier_id.fedex_bill_my_account', readonly=False)
    fedex_carrier_account = fields.Char(string='Fedex Carrier Account', readonly=False)
    ups_carrier_account = fields.Char(string='UPS Carrier Account', readonly=False)
    ups_service_type = fields.Selection(_get_ups_service_types, string="UPS Service Type")
    fedex_service_type = fields.Selection([('INTERNATIONAL_ECONOMY', 'INTERNATIONAL_ECONOMY'),
                                           ('INTERNATIONAL_PRIORITY', 'INTERNATIONAL_PRIORITY'),
                                           ('FEDEX_GROUND', 'FEDEX_GROUND'),
                                           ('FEDEX_2_DAY', 'FEDEX_2_DAY'),
                                           ('FEDEX_2_DAY_AM', 'FEDEX_2_DAY_AM'),
                                           ('FEDEX_3_DAY_FREIGHT', 'FEDEX_3_DAY_FREIGHT'),
                                           ('FIRST_OVERNIGHT', 'FIRST_OVERNIGHT'),
                                           ('PRIORITY_OVERNIGHT', 'PRIORITY_OVERNIGHT'),
                                           ('STANDARD_OVERNIGHT', 'STANDARD_OVERNIGHT')], string="Fedex Service Type")
    ups_bill_my_account = fields.Boolean(related='carrier_id.ups_bill_my_account', readonly=False)


    @api.multi
    @api.onchange('carrier_id')
    def _clear_shipping(self):
        if self.carrier_id.fedex_bill_my_account:
            self.ups_service_type = False
            self.ups_carrier_account = False
        else:
            self.fedex_carrier_account = False
            self.fedex_service_type = False

        if self.carrier_id.ups_bill_my_account:
            self.fedex_carrier_account = False
            self.fedex_service_type = False
        else:
            self.ups_service_type = False
            self.ups_carrier_account = False

