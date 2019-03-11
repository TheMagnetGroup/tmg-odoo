# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class MrpProduction(models.Model):
	_inherit = "mrp.production"

	job_id = fields.Many2one('mrp.job', string="Job reference in which this MO is included")