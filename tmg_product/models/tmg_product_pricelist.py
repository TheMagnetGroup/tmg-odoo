# -*- coding: utf-8 -*-

from odoo import models, fields, api

# from odoo.addons import decimal_precision as dp

class tmg_product_pricelist(models.Model):
    _inherit = 'product.pricelist'

    @api.multi
    def _compute_price_rule(self, products_qty_partner, date=False, uom_id=False):

        # First call Odoo's base _compute_price_rule to get the price without applying price extras
        result = super(PriceList, self)._compute_price_rule(products_qty_partner, date=date, uom_id=uom_id)

        # result is a dictionary of product_id: [price, rule_id]
        for pid in result:
            # if there is a rule:
            if result[pid][1]:
                rule_id = self.env['product.pricelist.item'].browse(result[pid][1])
                # if the rule has extra ids:
                if rule_id and rule_id.extra_ids:

                    d = {}
                    for e in rule_id.extra_ids:
                        d[e.attribute_id] = set(e.value_ids), e.price_extra

                    product_id = self.env['product.product'].browse(pid)

                    if product_id.attribute_value_ids:
                        for val in product_id.attribute_value_ids:
                            if val.attribute_id in d and val in d[val.attribute_id][0]:
                                result[pid] = result[pid][0] + d[val.attribute_id][1], result[pid][1]

        return result


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


