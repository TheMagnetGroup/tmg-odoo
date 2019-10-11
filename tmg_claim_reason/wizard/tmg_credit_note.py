# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountInvoiceRefund(models.TransientModel):
    _inherit = 'account.invoice.refund'
    claim_reason = fields.Many2many('claim.reason')



    @api.multi
    def compute_refund(self, mode='refund'):
        inv_obj = self.env['account.invoice']
        context = dict(self._context or {})
        res = super(AccountInvoiceRefund, self).compute_refund(mode=mode)
        for form in self:
            for inv in inv_obj.browse(context.get('active_ids')):
                # [EHE] here we just want to mark the original inv again
                xml_id = inv.type == 'out_invoice' and 'action_invoice_out_refund' or \
                    inv.type == 'out_refund' and 'action_invoice_tree1' or \
                    inv.type == 'in_invoice' and 'action_invoice_in_refund' or \
                    inv.type == 'in_refund' and 'action_invoice_tree2'
                if xml_id:
                    original_inv = inv
        if xml_id and mode == 'modify':
            original_inv.write({'claim_reason': self.claim_reason.id})
            original_inv.refund_invoice_ids.write({'claim_reason': self.claim_reason.id})
        return res

    @api.multi
    def invoice_refund(self):
        action_data = super(AccountInvoiceRefund,self).invoice_refund()
        if type(action_data) == dict:
            if self.filter_refund == 'modify':
                # invoices_ids = action_data['res_id']
                invoices_ids = []
            else:
                invoices_ids = action_data['domain'][-1][-1]
            if invoices_ids:
                invoice_ovj = self.env['account.invoice'].browse(invoices_ids)
                # invoice_ovj.write({'claim_reason': [(6, 0, [self.claim_reason.id])]})
                invoice_ovj.write({'claim_reason': self.claim_reason.id})
                if self.claim_reason.channel_id:
                    if self.filter_refund == 'modify':
                        self.action_send_notification(str(self.id))
                    else:
                        self.action_send_notification(invoice_ovj.origin)
        return action_data

    @api.constrains('claim_reason')
    @api.one
    def _check_claim_count(self):
        claims = self.claim_reason
        if len(claims) > 1:
            raise Warning("Can only have one claim on an invoice")

    @api.onchange('claim_reason')
    @api.multi
    def change_description(self):
        for record in self:
            if self.claim_reason:
                if len(self.claim_reason) >1:
                    raise Warning("Can only have one claim on an invoice")
                for claim in record.claim_reason:
                    record.description = claim.name
                    break
            else:
                record.description = ""


    @api.multi
    def action_send_notification(self, invoice_id):
        if self.claim_reason:
            if self.claim_reason.channel_id:
                channel_id = self.claim_reason.channel_id
                channel_id.message_post(subject='New claim created', body="A new claim has been created for the invoice" + invoice_id, subtype='mail.mt_comment')
