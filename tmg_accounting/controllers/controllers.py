# -*- coding: utf-8 -*-
from odoo import http

# class TmgAccounting(http.Controller):
#     @http.route('/tmg_accounting/tmg_accounting/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tmg_accounting/tmg_accounting/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('tmg_accounting.listing', {
#             'root': '/tmg_accounting/tmg_accounting',
#             'objects': http.request.env['tmg_accounting.tmg_accounting'].search([]),
#         })

#     @http.route('/tmg_accounting/tmg_accounting/objects/<model("tmg_accounting.tmg_accounting"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tmg_accounting.object', {
#             'object': obj
#         })