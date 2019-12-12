# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    fedex_bill_my_account = fields.Boolean(related='carrier_id.fedex_bill_my_account', readonly=True)
    fedex_carrier_account = fields.Char(related='sale_id.fedex_carrier_account', string='Fedex Carrier Account', readonly=False)
    ups_carrier_account = fields.Char(related='sale_id.ups_carrier_account', string='Carrier Account', readonly=False)
    ups_service_type = fields.Selection(related='sale_id.ups_service_type', string="UPS Service Type", readonly=False)
    fedex_service_type = fields.Selection(related='sale_id.fedex_service_type', string="Fedex Service Type")
    ups_bill_my_account = fields.Boolean(related='carrier_id.ups_bill_my_account', readonly=True)