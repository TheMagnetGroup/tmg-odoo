# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    scheduled_date = fields.Datetime(string='Scheduled Date', store=True, related='picking_id.scheduled_date')

# class tmg_stock_extensions(models.Model):
#     _name = 'tmg_stock_extensions.tmg_stock_extensions'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100

class Picking(models.Model):
    _inherit = "stock.picking"

    client_order_ref = fields.Char(string="Customer PO Ref",
                                   related='sale_id.client_order_ref',
                                   readonly="true")