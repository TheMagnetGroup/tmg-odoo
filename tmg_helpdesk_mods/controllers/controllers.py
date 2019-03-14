# -*- coding: utf-8 -*-
from odoo import http

# class /home/odoo/mods/helpdesk(http.Controller):
#     @http.route('//home/odoo/mods/helpdesk//home/odoo/mods/helpdesk/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('//home/odoo/mods/helpdesk//home/odoo/mods/helpdesk/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('/home/odoo/mods/helpdesk.listing', {
#             'root': '//home/odoo/mods/helpdesk//home/odoo/mods/helpdesk',
#             'objects': http.request.env['/home/odoo/mods/helpdesk./home/odoo/mods/helpdesk'].search([]),
#         })

#     @http.route('//home/odoo/mods/helpdesk//home/odoo/mods/helpdesk/objects/<model("/home/odoo/mods/helpdesk./home/odoo/mods/helpdesk"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('/home/odoo/mods/helpdesk.object', {
#             'object': obj
#         })