# -*- coding: utf-8 -*-
from odoo import http

# class TmgStockPickingBatch(http.Controller):
#     @http.route('/tmg_stock_picking_batch/tmg_stock_picking_batch/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tmg_stock_picking_batch/tmg_stock_picking_batch/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('tmg_stock_picking_batch.listing', {
#             'root': '/tmg_stock_picking_batch/tmg_stock_picking_batch',
#             'objects': http.request.env['tmg_stock_picking_batch.tmg_stock_picking_batch'].search([]),
#         })

#     @http.route('/tmg_stock_picking_batch/tmg_stock_picking_batch/objects/<model("tmg_stock_picking_batch.tmg_stock_picking_batch"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tmg_stock_picking_batch.object', {
#             'object': obj
#         })