# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    scheduled_date = fields.Datetime(string='Scheduled Date', store=True, related='picking_id.scheduled_date')

class Picking(models.Model):
    _inherit = "stock.picking"

    client_order_ref = fields.Char(string="Customer PO Ref",
                                   related='sale_id.client_order_ref',
                                   readonly="true")