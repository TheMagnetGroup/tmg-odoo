# -*- coding: utf-8 -*-
from odoo import http

# class TmgImportDelivery(http.Controller):
#     @http.route('/tmg_import_delivery/tmg_import_delivery/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tmg_import_delivery/tmg_import_delivery/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('tmg_import_delivery.listing', {
#             'root': '/tmg_import_delivery/tmg_import_delivery',
#             'objects': http.request.env['tmg_import_delivery.tmg_import_delivery'].search([]),
#         })

#     @http.route('/tmg_import_delivery/tmg_import_delivery/objects/<model("tmg_import_delivery.tmg_import_delivery"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tmg_import_delivery.object', {
#             'object': obj
#         })