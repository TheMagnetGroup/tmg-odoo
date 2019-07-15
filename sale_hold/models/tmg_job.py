# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions


class MrpJob(models.Model):
    _inherit = 'mrp.job'
    on_hold = fields.Boolean(string="On Hold")