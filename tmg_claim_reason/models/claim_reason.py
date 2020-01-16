# -*- coding: utf-8 -*-

from odoo import models, fields, api

class claim_reason(models.Model):
    _name = 'claim.reason'
    _description = 'Claim Reason'
    name = fields.Char(string="Name")
    description = fields.Char(string="Description")
    channel_id = fields.Many2one('mail.channel', 'Channel')
    # refund_ids = fields.Many2many('account.invoice.refund')
    invoices_ids = fields.One2many('account.invoice', 'claim_reason')
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100