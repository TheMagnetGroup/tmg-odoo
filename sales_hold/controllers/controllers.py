# -*- coding: utf-8 -*-
from odoo import http

# class SalesHold(http.Controller):
#     @http.route('/sales_hold/sales_hold/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sales_hold/sales_hold/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sales_hold.listing', {
#             'root': '/sales_hold/sales_hold',
#             'objects': http.request.env['sales_hold.sales_hold'].search([]),
#         })

#     @http.route('/sales_hold/sales_hold/objects/<model("sales_hold.sales_hold"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sales_hold.object', {
#             'object': obj
#         })