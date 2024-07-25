# Copyright 2021 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).

from odoo import models, fields, api, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'


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

#     def action_confirm(self):
#         res = super(SaleOrder, self).action_confirm()
#         for sale in self:
#             if sale.shipping_term in ('collect', 'free', 'thirdparty', 'cod'):
#                 sale.invoice_shipping_on_delivery = False
#         return res

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals['shipping_term'] = self.shipping_term
        return invoice_vals

    @api.onchange('shipping_term')
    def add_cod_product(self):
        product_id = int(self.env['ir.config_parameter'].sudo().get_param('product_id'))
        if self.shipping_term == 'cod' and not product_id:
            self.shipping_term = 'prepaid_add'
            return {
                    'warning': {
                                'title': _('Warning'),
                                'message': _('Please configure C.O.D. Product under Sale Settings')
                                }
                    }
        if product_id:
            product = self.env["product.product"].browse(product_id)
            cod_order_line = self.order_line.filtered(lambda x: x.product_id == product)
            so_line = [(4, line.id) for line in self.order_line]
            if self.shipping_term == 'cod' and not cod_order_line:
                so_line += [(0, 0, {
                        'product_id': product.id,
                        'name': product.name,
                        'product_uom_qty': 1,
                        'product_uom': product.uom_id.id,
                        'price_unit': product.lst_price,
                        'tax_id': [(6, 0, [x.id for x in product.taxes_id])]})]
                self.order_line = so_line
            if self.shipping_term != 'cod' and cod_order_line:
                so_line += [(2, cod_order_line.id, 0)]
                self.order_line = so_line

    @api.onchange('partner_id')
    def onchange_partner(self):
        self.carrier_id = self.partner_id.property_delivery_carrier_id
        self.shipping_term = self.partner_id.shipping_term
        self.third_party_billing_id = self.partner_id.third_party_billing_id
        self.carrier_account = self.partner_id.carrier_account

    @api.onchange('partner_shipping_id')
    def onchange_partner_shipping(self):
        if self.partner_shipping_id.property_delivery_carrier_id:
            self.carrier_id = self.partner_shipping_id.property_delivery_carrier_id
            self.shipping_term = self.partner_shipping_id.shipping_term
            self.third_party_billing_id = self.partner_shipping_id.third_party_billing_id
            self.carrier_account = self.partner_shipping_id.carrier_account
        else:
            self.carrier_id = self.partner_id.property_delivery_carrier_id
            self.shipping_term = self.partner_id.shipping_term
            self.third_party_billing_id = self.partner_id.third_party_billing_id
            self.carrier_account = self.partner_id.carrier_account

