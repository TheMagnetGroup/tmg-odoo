# -*- coding: utf-8 -*-
from odoo import http

# class TmgStockRule(http.Controller):
#     @http.route('/tmg_stock_rule/tmg_stock_rule/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tmg_stock_rule/tmg_stock_rule/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('tmg_stock_rule.listing', {
#             'root': '/tmg_stock_rule/tmg_stock_rule',
#             'objects': http.request.env['tmg_stock_rule.tmg_stock_rule'].search([]),
#         })

#     @http.route('/tmg_stock_rule/tmg_stock_rule/objects/<model("tmg_stock_rule.tmg_stock_rule"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tmg_stock_rule.object', {
#             'object': obj
#         })