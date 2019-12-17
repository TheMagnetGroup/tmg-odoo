# -*- coding: utf-8 -*-
from odoo import http

# class /home/odoo/mods/tmg-odoo/tmgPurcashing(http.Controller):
#     @http.route('//home/odoo/mods/tmg-odoo/tmg_purcashing//home/odoo/mods/tmg-odoo/tmg_purcashing/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('//home/odoo/mods/tmg-odoo/tmg_purcashing//home/odoo/mods/tmg-odoo/tmg_purcashing/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('/home/odoo/mods/tmg-odoo/tmg_purcashing.listing', {
#             'root': '//home/odoo/mods/tmg-odoo/tmg_purcashing//home/odoo/mods/tmg-odoo/tmg_purcashing',
#             'objects': http.request.env['/home/odoo/mods/tmg-odoo/tmg_purcashing./home/odoo/mods/tmg-odoo/tmg_purcashing'].search([]),
#         })

#     @http.route('//home/odoo/mods/tmg-odoo/tmg_purcashing//home/odoo/mods/tmg-odoo/tmg_purcashing/objects/<model("/home/odoo/mods/tmg-odoo/tmg_purcashing./home/odoo/mods/tmg-odoo/tmg_purcashing"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('/home/odoo/mods/tmg-odoo/tmg_purcashing.object', {
#             'object': obj
#         })