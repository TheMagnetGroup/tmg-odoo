# -*- coding: utf-8 -*-
import logging
import time
from datetime import date, datetime, timedelta

from odoo import api, fields, models, _, exceptions


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    sale_line_id = fields.Many2one('sale.order.line' ,ondelete='set null', string='Corresponsding Sale Order Line')
    sale_line_order_id = fields.Many2one(string='Sales Order',ondelete='set null',  comodel_name='sale.order', related='sale_line_id.order_id')
    sale_line_attr_value_id= fields.Many2many(related='sale_line_id.product_no_variant_attribute_value_ids', string="Sale Line Atributes")
    sale_line_description= fields.Text(related="sale_line_id.name", string="Sale Line Description")
    sale_notes = fields.Html(related='sale_line_order_id.order_notes', string="Sales Order Notes")
    product_category = fields.Many2one(related="product_id.categ_id", string="Product Category", store=True, copy=True)
    def _generate_finished_moves(self):
        move = super(MrpProduction, self)._generate_finished_moves()
        move.sale_line_id = self.sale_line_id
        return move

    def _generate_raw_move(self, bom_line, line_data):
        move = super(MrpProduction, self)._generate_raw_move(bom_line, line_data)
        move.sale_line_id = self.sale_line_id
        return move




