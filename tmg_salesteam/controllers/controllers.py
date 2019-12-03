# -*- coding: utf-8 -*-
from odoo import http

# class TmgSalesteam(http.Controller):
#     @http.route('/tmg_salesteam/tmg_salesteam/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tmg_salesteam/tmg_salesteam/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('tmg_salesteam.listing', {
#             'root': '/tmg_salesteam/tmg_salesteam',
#             'objects': http.request.env['tmg_salesteam.tmg_salesteam'].search([]),
#         })

#     @http.route('/tmg_salesteam/tmg_salesteam/objects/<model("tmg_salesteam.tmg_salesteam"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tmg_salesteam.object', {
#             'object': obj
#         })