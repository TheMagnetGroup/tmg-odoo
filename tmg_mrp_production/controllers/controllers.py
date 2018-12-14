# -*- coding: utf-8 -*-
from odoo import http

# class TmgMrpProduction(http.Controller):
#     @http.route('/tmg_mrp_production/tmg_mrp_production/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tmg_mrp_production/tmg_mrp_production/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('tmg_mrp_production.listing', {
#             'root': '/tmg_mrp_production/tmg_mrp_production',
#             'objects': http.request.env['tmg_mrp_production.tmg_mrp_production'].search([]),
#         })

#     @http.route('/tmg_mrp_production/tmg_mrp_production/objects/<model("tmg_mrp_production.tmg_mrp_production"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tmg_mrp_production.object', {
#             'object': obj
#         })