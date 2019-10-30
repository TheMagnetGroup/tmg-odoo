# -*- coding: utf-8 -*-


# my to-do list:    change mod name to tmg_identifiers

from odoo import models, fields, api


class tmg_industry_identifiers(models.Model):
    _inherit = 'res.partner'

    asi_number = fields.Char(string="ASI Number")
    sage_number = fields.Char(string="Sage Number")
    ppai_number = fields.Char(string="PPAI Number")
