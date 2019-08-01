# -*- coding: utf-8 -*-

from odoo import models, fields, api


class tmg_customer(models.Model):

    _inherit = 'res.partner'

    tmg_customer_rebate = fields.Boolean()