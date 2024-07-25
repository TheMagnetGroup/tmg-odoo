# Copyright 2021 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).

from odoo import models, fields, api


class Partner(models.Model):
    _inherit = 'res.partner'


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

    def _get_default_ship_term(self):
        if self.env['ir.config_parameter'].sudo().get_param('prepaid_add'):
            return 'prepaid_add'

    shipping_term = fields.Selection(_get_ship_terms , string='Shipping Terms', copy=False, default=_get_default_ship_term)
    third_party_billing_id = fields.Many2one('res.partner', string='3rd party billing', copy=False)
    carrier_account = fields.Char(string='Carrier Account', copy=False)