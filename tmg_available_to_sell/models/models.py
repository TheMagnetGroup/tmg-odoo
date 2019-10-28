# -*- coding: utf-8 -*-

from odoo import models, fields, api

# class tmg_available_to_sell(models.Model):
#     _name = 'tmg_available_to_sell.tmg_available_to_sell'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100