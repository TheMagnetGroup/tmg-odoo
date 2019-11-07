# -*- coding: utf-8 -*-
from odoo import http

# class TmgAttachmentTypes(http.Controller):
#     @http.route('/tmg_attachment_types/tmg_attachment_types/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tmg_attachment_types/tmg_attachment_types/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('tmg_attachment_types.listing', {
#             'root': '/tmg_attachment_types/tmg_attachment_types',
#             'objects': http.request.env['tmg_attachment_types.tmg_attachment_types'].search([]),
#         })

#     @http.route('/tmg_attachment_types/tmg_attachment_types/objects/<model("tmg_attachment_types.tmg_attachment_types"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tmg_attachment_types.object', {
#             'object': obj
#         })