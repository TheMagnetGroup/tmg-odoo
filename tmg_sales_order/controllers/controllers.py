# -*- coding: utf-8 -*-
from odoo import http

# class TmgSalesOrder(http.Controller):
#     @http.route('/tmg_sales_order/tmg_sales_order/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tmg_sales_order/tmg_sales_order/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('tmg_sales_order.listing', {
#             'root': '/tmg_sales_order/tmg_sales_order',
#             'objects': http.request.env['tmg_sales_order.tmg_sales_order'].search([]),
#         })

#     @http.route('/tmg_sales_order/tmg_sales_order/objects/<model("tmg_sales_order.tmg_sales_order"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tmg_sales_order.object', {
#             'object': obj
#         })