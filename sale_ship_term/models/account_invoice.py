# Copyright 2021 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).

from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'
    
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