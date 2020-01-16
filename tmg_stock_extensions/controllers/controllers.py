# -*- coding: utf-8 -*-
from odoo import http

# class TmgStockExtensions(http.Controller):
#     @http.route('/tmg_stock_extensions/tmg_stock_extensions/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tmg_stock_extensions/tmg_stock_extensions/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('tmg_stock_extensions.listing', {
#             'root': '/tmg_stock_extensions/tmg_stock_extensions',
#             'objects': http.request.env['tmg_stock_extensions.tmg_stock_extensions'].search([]),
#         })

#     @http.route('/tmg_stock_extensions/tmg_stock_extensions/objects/<model("tmg_stock_extensions.tmg_stock_extensions"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tmg_stock_extensions.object', {
#             'object': obj
#         })