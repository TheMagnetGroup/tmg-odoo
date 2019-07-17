# -*- coding: utf-8 -*-
from odoo import http

# class TmgSoInhands(http.Controller):
#     @http.route('/tmg_so_inhands/tmg_so_inhands/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tmg_so_inhands/tmg_so_inhands/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('tmg_so_inhands.listing', {
#             'root': '/tmg_so_inhands/tmg_so_inhands',
#             'objects': http.request.env['tmg_so_inhands.tmg_so_inhands'].search([]),
#         })

#     @http.route('/tmg_so_inhands/tmg_so_inhands/objects/<model("tmg_so_inhands.tmg_so_inhands"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tmg_so_inhands.object', {
#             'object': obj
#         })