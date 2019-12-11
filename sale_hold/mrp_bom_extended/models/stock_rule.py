# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _prepare_mo_vals(self, product_id, product_qty, product_uom, location_id, name, origin, values, bom):
        result = super(StockRule, self)._prepare_mo_vals(product_id, product_qty, product_uom, location_id, name, origin, values, bom)
        result.update({'inactive_attribute_value_ids': values.get('inactive_attribute_value_ids')})
        return result

    def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name, origin, values, group_id):
        result = super(StockRule, self)._get_stock_move_values(product_id, product_qty, product_uom, location_id, name, origin, values, group_id)
        result.update({'inactive_attribute_value_ids': values.get('inactive_attribute_value_ids')})
        return result
