# -*- coding: utf-8 -*-
from odoo import http

# class TmgSale(http.Controller):
#     @http.route('/tmg_sale/tmg_sale/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tmg_sale/tmg_sale/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('tmg_sale.listing', {
#             'root': '/tmg_sale/tmg_sale',
#             'objects': http.request.env['tmg_sale.tmg_sale'].search([]),
#         })

#     @http.route('/tmg_sale/tmg_sale/objects/<model("tmg_sale.tmg_sale"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tmg_sale.object', {
#             'object': obj
#         })