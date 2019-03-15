# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    job_id = fields.Many2one("mrp.job", string="Job Reference")
