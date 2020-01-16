# -*- coding: utf-8 -*-

from odoo import models, fields, api

class tmg_salesperson(models.Model):
    _inherit= 'sale.order'

    user_id= fields.Many2one(string='Customer Service Rep')

    salesperson_id = fields.Many2one('res.users', string='Salesperson', index=True, track_visibility='onchange')
