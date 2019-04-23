# -*- coding: utf-8 -*-

from odoo import models, fields, api

# from odoo.addons import decimal_precision as dp

class tmg_product_pricelist_item(models.Model):
    _inherit = 'product.pricelist.item'

    extra_ids = fields.One2many('product.pricelist.item.extras', 'pricelist_item_id', string="Price Extras", copy=True)


class tmg_product_pricelist_item_extra(models.Model):
    _name = 'product.pricelist.item.extras'
    _description = "Pricelist Item Extras"

    pricelist_item_id = fields.Many2one(
        'product.pricelist.item','Product Pricelist Item', ondelete='cascade',
        help='The pricelist item this attribute extra price is associated with')

    price_extra = fields.Float(
        'Attribute Price Extra', digits=(10,2),
        help='The additional price this attribute extra adds to the product price')

    attribute_id = fields.Many2one('product.attribute', string='Attribute', ondelete='restrict', required=True)
    value_ids = fields.Many2many('product.attribute.value', string='Attribute Values')


