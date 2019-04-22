# -*- coding: utf-8 -*-

from odoo import api, fields, models


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    job_id = fields.Many2one(related="production_id.job_id", string="Job Reference")
