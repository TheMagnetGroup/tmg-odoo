# -*- coding: utf-8 -*-

from odoo import models, fields, api

class tmg_proofing(models.Model):
    _name = 'sale.tmg_proofing'
    id = fields.Integer(string="ID")

    name = fields.Char(string="Name")
    art_file = fields.Many2one("ir.attachments", string="ArtFiles")
    sale_line = fields.Many2one("sale.order.line", string = "Sale Line")
    sale_order = fields.Many2one('sale.order',related='sale_line.order_id')
    proofing_link = fields.Char(string = "Proof Link")
    original_date = fields.Datetime(string= "Original Date")
    notes = fields.Html('Order Notes')
    state = fields.Selection(
        [("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected"), ("approved_with_changes", "Approved With Changes")],
        "Proof State",
        default="pending",
    )

    @api.depends('value')
    def _value_pc(self):
        self.value2 = float(self.value) / 100