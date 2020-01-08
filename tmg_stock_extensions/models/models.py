# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    scheduled_date = fields.Datetime(string='Scheduled Date', store=True, related='picking_id.scheduled_date')

