# -*- coding: utf-8 -*-
from odoo import http

# class TmgInHands(http.Controller):
#     @http.route('/tmg_in_hands/tmg_in_hands/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tmg_in_hands/tmg_in_hands/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('tmg_in_hands.listing', {
#             'root': '/tmg_in_hands/tmg_in_hands',
#             'objects': http.request.env['tmg_in_hands.tmg_in_hands'].search([]),
#         })

#     @http.route('/tmg_in_hands/tmg_in_hands/objects/<model("tmg_in_hands.tmg_in_hands"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tmg_in_hands.object', {
#             'object': obj
#         })