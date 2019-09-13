# -*- coding: utf-8 -*-
from odoo import http

# class TmgIndustryIdentifiers(http.Controller):
#     @http.route('/tmg_industry_identifiers/tmg_industry_identifiers/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tmg_industry_identifiers/tmg_industry_identifiers/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('tmg_industry_identifiers.listing', {
#             'root': '/tmg_industry_identifiers/tmg_industry_identifiers',
#             'objects': http.request.env['tmg_industry_identifiers.tmg_industry_identifiers'].search([]),
#         })

#     @http.route('/tmg_industry_identifiers/tmg_industry_identifiers/objects/<model("tmg_industry_identifiers.tmg_industry_identifiers"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tmg_industry_identifiers.object', {
#             'object': obj
#         })