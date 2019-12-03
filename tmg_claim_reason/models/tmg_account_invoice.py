# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    claim_reason = fields.Many2one('claim.reason',string="Claim Reason", track_visibility='onchange', copy=False)


    @api.constrains('claim_reason')
    @api.one
    def _check_claim_count(self):
        claims = self.claim_reason
        if len(claims) > 1:
            raise Warning("Can only have one claim on an invoice")