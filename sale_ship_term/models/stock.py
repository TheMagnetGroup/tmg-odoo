# Copyright 2021 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).

from odoo import models, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    def _get_ship_terms(self):
        res = []
        shipping_options = [('prepaid_add', 'Prepaid & Add'),
                 ('collect', 'Collect'),
                 ('free', 'Free'),
                 ('thirdparty', 'Bill 3rd party'),
                 ('cod', 'C.O.D.')]
        for option in shipping_options:
            if self.env['ir.config_parameter'].sudo().get_param(option[0]):
                res.append(option)
        return res

    shipping_term = fields.Selection(_get_ship_terms , string='Shipping Terms')
    third_party_billing_id = fields.Many2one('res.partner', string='3rd party billing')
    carrier_account = fields.Char(string='Carrier Account')
    cod_amount = fields.Float(string='C.O.D Amount', copy=False, readonly=True)

    def _add_delivery_cost_to_so(self):
        self.ensure_one()
        if self.shipping_term not in ('collect', 'free', 'thirdparty', 'cod') and self.sale_id and self.carrier_id:
            super()._add_delivery_cost_to_so()
