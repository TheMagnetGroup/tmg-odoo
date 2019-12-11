# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    inactive_attribute_value_ids = fields.Many2many(
        'product.attribute.value', string='Inactive Variant Attributes',
        help="Product Variants used on configurator that set no create and will be used in selection of the raw materials.")

    def _prepare_procurement_values(self):
        result = super(StockMove, self)._prepare_procurement_values()
        result.update({'inactive_attribute_value_ids': [(4, avi.id) for avi in self.inactive_attribute_value_ids]})
        return result
