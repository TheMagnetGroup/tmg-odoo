# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, exceptions


# We don't really do anything to sale order,
# We use this model only in order to set a breakpoint and debug
class SaleOrder(models.Model):
    _inherit = 'sale.order'
    order_notes = fields.Html('Order Notes')
    production_ids = fields.One2many("mrp.production", "sale_line_order_id",ondelete='set null', string="Production Orders")
    production_count = fields.Integer(compute="_get_production_count")

    @api.depends('order_line')
    def _get_production_count(self):
        if self.production_ids:
            self.production_count = len(self.production_ids)

#     # what happens when you confirm a sale order?
#     def action_confirm(self):
#         res = super(SaleOrder, self).action_confirm()
#         return res
class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    production_order = fields.One2many('mrp.production', "sale_line_id", ondelete='set null')
