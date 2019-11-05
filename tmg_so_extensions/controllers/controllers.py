# -*- coding: utf-8 -*-
from odoo import http

# class TmgSoExtensions(http.Controller):
#     @http.route('/tmg_so_extensions/tmg_so_extensions/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tmg_so_extensions/tmg_so_extensions/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('tmg_so_extensions.listing', {
#             'root': '/tmg_so_extensions/tmg_so_extensions',
#             'objects': http.request.env['tmg_so_extensions.tmg_so_extensions'].search([]),
#         })

#     @http.route('/tmg_so_extensions/tmg_so_extensions/objects/<model("tmg_so_extensions.tmg_so_extensions"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tmg_so_extensions.object', {
#             'object': obj
#         })