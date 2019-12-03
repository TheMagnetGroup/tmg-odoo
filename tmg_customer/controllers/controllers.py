# -*- coding: utf-8 -*-
from odoo import http

# class TmgCustomer(http.Controller):
#     @http.route('/tmg_customer/tmg_customer/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tmg_customer/tmg_customer/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('tmg_customer.listing', {
#             'root': '/tmg_customer/tmg_customer',
#             'objects': http.request.env['tmg_customer.tmg_customer'].search([]),
#         })

#     @http.route('/tmg_customer/tmg_customer/objects/<model("tmg_customer.tmg_customer"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tmg_customer.object', {
#             'object': obj
#         })