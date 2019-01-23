# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, exceptions


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    sale_line_id = fields.Many2one('sale.order.line', ondelete='set null', string='Sales Order Line')
    sale_line_description = fields.Text(related="sale_line_id.name")
    sale_line_attr_value_ids = fields.Many2many(related='sale_line_id.product_no_variant_attribute_value_ids')

    sale_line_order_id = fields.Many2one(string='Sales  Order', comodel_name='sale.order', related='sale_line_id.order_id')

    def _generate_finished_moves(self):
        move = super(MrpProduction, self)._generate_finished_moves()
        move.sale_line_id = self.sale_line_id
        return move

    def _generate_raw_move(self, bom_line, line_data):
        move = super(MrpProduction, self)._generate_raw_move(bom_line, line_data)
        move.sale_line_id = self.sale_line_id
        return move
