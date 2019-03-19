# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    inactive_attribute_value_ids = fields.Many2many(
        'product.attribute.value', string='Inactive Variant Attributes',
        help="Product Variants used on configurator that set no create and will be used in selection of the raw materials.")

    @api.multi
    def _generate_moves(self):
        for production in self:
            production._generate_finished_moves()
            factor = production.product_uom_id._compute_quantity(production.product_qty, production.bom_id.product_uom_id) / production.bom_id.product_qty
            boms, lines = production.bom_id.with_context(inactive_attribute_value_ids=production.inactive_attribute_value_ids).explode(production.product_id, factor, picking_type=production.bom_id.picking_type_id)
            production._generate_raw_moves(lines)
            # Check for all draft moves whether they are mto or not
            production._adjust_procure_method()
            production.move_raw_ids._action_confirm()
        return True
