# -*- coding: utf-8 -*-

from odoo import models, fields, api


class tmg_mrp_production(models.Model):
    _inherit = 'mrp.production'
    sale_line_id = fields.Many2one(related='move_dest_ids.sale_line_id', store="True")
    sale_line_description = fields.Text(related="move_dest_ids.sale_line_id.name")

    sale_line_attr_value_ids = fields.Many2many(related='move_dest_ids.sale_line_id.product_no_variant_attribute_value_ids')
    #sale_notes = fields.Text(related='move_dest_ids.sale_line_id.order_id.order_notes')
    sale_line_order_id = fields.Many2one(string='Sales  Order', comodel_name='sale.order', related='move_dest_ids.sale_line_id.order_id' , store='True')
  #  sale_notes = fields.Char(related="move_dest_ids.sale_line_id.order_id.order_notes")

	
