# -*- coding: utf-8 -*-
from odoo import http

# class TmgAvailableToSell(http.Controller):
#     @http.route('/tmg_available_to_sell/tmg_available_to_sell/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tmg_available_to_sell/tmg_available_to_sell/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('tmg_available_to_sell.listing', {
#             'root': '/tmg_available_to_sell/tmg_available_to_sell',
#             'objects': http.request.env['tmg_available_to_sell.tmg_available_to_sell'].search([]),
#         })

#     @http.route('/tmg_available_to_sell/tmg_available_to_sell/objects/<model("tmg_available_to_sell.tmg_available_to_sell"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tmg_available_to_sell.object', {
#             'object': obj
#         })