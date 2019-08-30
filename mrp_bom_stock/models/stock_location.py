# -*- coding: utf-8 -*-

from odoo import api, fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse', default=lambda self: self.env['stock.warehouse'].sudo().search([], limit=1))

    @api.model
    def create(self, vals):
        location = super(StockLocation, self).create(vals)
        if location.location_id:
            location.warehouse_id = location.get_warehouse()
        return location

    @api.multi
    def write(self, vals):
        res = super(StockLocation, self).write(vals)
        for location in self.filtered(lambda l: l.location_id and not l.warehouse_id):
            location.warehouse_id = location.get_warehouse()
        return res
