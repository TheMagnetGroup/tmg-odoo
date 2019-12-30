# -*- coding: utf-8 -*-

from odoo import api, fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse', default=lambda self: self.env['stock.warehouse'].sudo().search([], limit=1))

    @api.model
    def create(self, vals):
        location = super(StockLocation, self).create(vals)
        if location.location_id and location.usage == 'internal':
            wh = False
            if location.location_id.warehouse_id:
                wh = location.location_id.warehouse_id
            else:
                warehouses = self.env['stock.warehouse'].sudo().search([])
                view_loc = False
                loc = location
                while not view_loc:
                    if loc.usage == 'view':
                        view_loc = loc
                    if not location.location_id:
                        break
                    loc = location.location_id
                if view_loc:
                    wh = warehouses.filtered(lambda w: w.view_location_id == view_loc)
            location.warehouse_id = wh
        return location

    @api.multi
    def write(self, vals):
        res = super(StockLocation, self).write(vals)
        if 'location_id' in vals.keys():
            for location in self.filtered(lambda l: l.location_id and l.usage == 'internal'):
                wh = False
                if location.location_id.warehouse_id:
                    wh = location.location_id.warehouse_id
                else:
                    warehouses = self.env['stock.warehouse'].sudo().search([])
                    view_loc = False
                    loc = location
                    while not view_loc:
                        if loc.usage == 'view':
                            view_loc = loc
                        if not location.location_id:
                            break
                        loc = location.location_id
                    if view_loc:
                        wh = warehouses.filtered(lambda w: w.view_location_id == view_loc)
                location.warehouse_id = wh
        return res


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    @api.model
    def create(self, vals):
        warehouse = super(StockWarehouse, self).create(vals)
        sub_locations = self._get_locations_values(vals)
        for loc_field in list(sub_locations.keys()) + ['view_location_id']:
            warehouse[loc_field].warehouse_id = warehouse
        return warehouse