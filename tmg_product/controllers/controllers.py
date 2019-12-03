# -*- coding: utf-8 -*-
from odoo import http

# class TmgProduct(http.Controller):
#     @http.route('/tmg_product/tmg_product/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tmg_product/tmg_product/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('tmg_product.listing', {
#             'root': '/tmg_product/tmg_product',
#             'objects': http.request.env['tmg_product.tmg_product'].search([]),
#         })

#     @http.route('/tmg_product/tmg_product/objects/<model("tmg_product.tmg_product"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tmg_product.object', {
#             'object': obj
#         })