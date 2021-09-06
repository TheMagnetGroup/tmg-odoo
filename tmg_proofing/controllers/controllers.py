# -*- coding: utf-8 -*-
from odoo import http

# class TmgProofing(http.Controller):
#     @http.route('/tmg_proofing/tmg_proofing/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tmg_proofing/tmg_proofing/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('tmg_proofing.listing', {
#             'root': '/tmg_proofing/tmg_proofing',
#             'objects': http.request.env['tmg_proofing.tmg_proofing'].search([]),
#         })

#     @http.route('/tmg_proofing/tmg_proofing/objects/<model("tmg_proofing.tmg_proofing"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tmg_proofing.object', {
#             'object': obj
#         })