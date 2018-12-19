# -*- coding: utf-8 -*-

from odoo import models, fields, api


class tmg_sales_order(models.Model):
    _inherit = "sale.order"
    order_notes = fields.Html('Order Notes')
    production_ids = fields.One2many("mrp.production","sale_line_order_id", string="Production")
    production_count = fields.Integer(compute="_get_production_count")

    @api.one
    def _get_production_count(self):
        if self.production_ids:
            self.production_count = len(self.production_ids)









