# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, exceptions


class MrpProduction(models.Model):
    _inherit = "sale.order"
    order_notes = fields.Text('Order Notes')
    production_ids = fields.One2many("mrp.production", "sale_line_order_id", string="Production")
    production_count = fields.Integer(compute="_get_production_count")



    @api.depends('order_line')
    def _get_production_count(self):
        if self.production_ids:
            self.production_count = len(self.production_ids)
        else:
            print("NotFound")




class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    production_order = fields.One2many('mrp.production', "sale_line_id", string="Production Orders", store="True")














