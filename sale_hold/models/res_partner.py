# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

class Partner(models.Model):
    _inherit = "res.partner"
    credit_limit = fields.Monetary(string="Credit Limit")