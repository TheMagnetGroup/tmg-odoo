# -*- coding: utf-8 -*-
from odoo import http

# class TmgExternalApis(http.Controller):
#     @http.route('/tmg_external_apis/tmg_external_apis/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tmg_external_apis/tmg_external_apis/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('tmg_external_apis.listing', {
#             'root': '/tmg_external_apis/tmg_external_apis',
#             'objects': http.request.env['tmg_external_apis.tmg_external_apis'].search([]),
#         })

#     @http.route('/tmg_external_apis/tmg_external_apis/objects/<model("tmg_external_apis.tmg_external_apis"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tmg_external_apis.object', {
#             'object': obj
#         })