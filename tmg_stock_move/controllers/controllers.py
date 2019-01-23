# -*- coding: utf-8 -*-
from odoo import http

# class TmgStockMove(http.Controller):
#     @http.route('/tmg_stock_move/tmg_stock_move/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tmg_stock_move/tmg_stock_move/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('tmg_stock_move.listing', {
#             'root': '/tmg_stock_move/tmg_stock_move',
#             'objects': http.request.env['tmg_stock_move.tmg_stock_move'].search([]),
#         })

#     @http.route('/tmg_stock_move/tmg_stock_move/objects/<model("tmg_stock_move.tmg_stock_move"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tmg_stock_move.object', {
#             'object': obj
#         })