# -*- coding: utf-8 -*-
from odoo import http

# class TmgCrm(http.Controller):
#     @http.route('/tmg_crm/tmg_crm/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tmg_crm/tmg_crm/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('tmg_crm.listing', {
#             'root': '/tmg_crm/tmg_crm',
#             'objects': http.request.env['tmg_crm.tmg_crm'].search([]),
#         })

#     @http.route('/tmg_crm/tmg_crm/objects/<model("tmg_crm.tmg_crm"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tmg_crm.object', {
#             'object': obj
#         })