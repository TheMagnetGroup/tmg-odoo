# -*- coding: utf-8 -*-
from odoo import http

# class TmgSalesperson(http.Controller):
#     @http.route('/tmg_salesperson/tmg_salesperson/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tmg_salesperson/tmg_salesperson/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('tmg_salesperson.listing', {
#             'root': '/tmg_salesperson/tmg_salesperson',
#             'objects': http.request.env['tmg_salesperson.tmg_salesperson'].search([]),
#         })

#     @http.route('/tmg_salesperson/tmg_salesperson/objects/<model("tmg_salesperson.tmg_salesperson"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tmg_salesperson.object', {
#             'object': obj
#         })