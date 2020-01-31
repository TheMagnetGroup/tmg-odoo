# -*- coding: utf-8 -*-

from odoo import models, fields, api


class tmg_in_hands(models.Model):
    _inherit = "sale.order"

    in_hands = fields.Date('In Hands Date', readonly=True)
