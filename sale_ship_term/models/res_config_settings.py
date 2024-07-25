# Copyright 2021 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).

from ast import literal_eval
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        res.update(
            prepaid_add=ICPSudo.get_param('prepaid_add'),
            collect=ICPSudo.get_param('collect'),
            free=ICPSudo.get_param('free'),
            thirdparty=ICPSudo.get_param('thirdparty'),
            cod=ICPSudo.get_param('cod'),
            product_id=literal_eval(ICPSudo.get_param('product_id', default='False')),
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param('product_id', self.product_id.id)
        un_check = []
        if not self.prepaid_add:
            un_check.append('prepaid_add')
        ICPSudo.set_param('prepaid_add', self.prepaid_add)
        if not self.collect:
            un_check.append('collect')
        ICPSudo.set_param('collect', self.collect)

        if not self.free:
            un_check.append('free')
        ICPSudo.set_param('free', self.free)

        if not self.thirdparty:
            un_check.append('thirdparty')
        ICPSudo.set_param('thirdparty', self.thirdparty)

        if not self.cod:
            un_check.append('cod')
        ICPSudo.set_param('cod', self.cod)
        
        if self.env['sale.order'].search([('shipping_term', 'in', un_check)]):
            raise UserError(_('Some of the shipping terms are used in Sales order. So we cannot remove that shipping term!!! '))
        if self.env['stock.picking'].search([('shipping_term', 'in', un_check)]):
            raise UserError(_('Some of the shipping terms are used in Delivery order. So we cannot remove that shipping term!!! '))
        if self.env['account.move'].search([('shipping_term', 'in', un_check)]):
            raise UserError(_('Some of the shipping terms are used in Invoice. So we cannot remove that shipping term!!! '))
        if self.env['res.partner'].search([('shipping_term', 'in', un_check)]):
            raise UserError(_('Some of the shipping terms are used in partner. So we cannot remove that shipping term!!! '))

    prepaid_add = fields.Boolean(string='Prepaid & Add')
    collect = fields.Boolean()
    free = fields.Boolean()
    thirdparty = fields.Boolean(string='Bill 3rd party', help="Billing address for the 3rd party")
    cod = fields.Boolean(string='C.O.D.')
    product_id = fields.Many2one('product.product', string='C.O.D. Product',
        help="When COD shipping term is selected, this product will be added to the sales order line")
