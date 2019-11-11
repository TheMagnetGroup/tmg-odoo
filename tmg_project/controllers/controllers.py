# -*- coding: utf-8 -*-
from odoo import http

# class TmgProject(http.Controller):
#     @http.route('/tmg_project/tmg_project/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tmg_project/tmg_project/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('tmg_project.listing', {
#             'root': '/tmg_project/tmg_project',
#             'objects': http.request.env['tmg_project.tmg_project'].search([]),
#         })

#     @http.route('/tmg_project/tmg_project/objects/<model("tmg_project.tmg_project"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tmg_project.object', {
#             'object': obj
#         })