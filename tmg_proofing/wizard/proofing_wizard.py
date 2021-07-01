# -*- coding: utf-8 -*-
import base64
from odoo import models, fields, api, exceptions
from odoo.exceptions import AccessError, UserError, RedirectWarning, \
    ValidationError, Warning
from odoo.exceptions import ValidationError
import re


class SaleOrderLineSendProofWizard(models.TransientModel):
    _name = 'sale.order.line.send.proof.wizard'
    _description = 'sale order line proof entry wizard'
    # explicitly pass in context

    def _default_sol(self):
        return self.env['sale.order.line'].browse(self.env.context.get('active_ids'))[0]
    sale_line_id = fields.Many2one('sale.order.line', string='Active SOLs', ondelete='cascade', required=True, default=_default_sol)
    sale_order = fields.Many2one('sale.order', related='sale_line_id.order_id')
    # attachment_ids = fields.One2many('ir.attachment', compute='_compute_attachment_ids',
    #                                   string="Main Attachments")
    art_file = fields.Many2one("ir.attachment", string="ArtFiles",
                               domain="[('res_id','in',[sale_order]),('type', '=', 'url')]")
    suggested_layout = fields.Boolean(string="Suggested Layout")
    email_ids = fields.Many2many('res.partner', string="Send To")
    send_attachments = fields.Boolean(string="Send Attachments", default=False)

    # @api.constrains('ups_service_type')
    # def _validate_account(self):
    #     if self.ups_service_type:
    #         if not self.ups_carrier_id and self.ups_bill_my_account:
    #             raise ValidationError("You cannot select a third party shipper without supplying an account number")

    def check_active_proof(self):
        proofs = any(l.state == 'pending' for l in self.sale_line_id.proofing_lines)
        if proofs:
            raise UserError('Please resolve pending proofs before creating new ones.')

    # def _compute_attachment_ids(self):
    #     for order in self:
    #         soID = self._default_sol().order_id
    #         attachment_idss = self.env['ir.attachment'].search([('res_id', '=', soID.id), ('res_model', '=', 'sale.order')]).ids
    #         message_attachment_ids = soID.mapped('message_ids.attachment_ids').ids  # from mail_thread
    #         ids = list(set(attachment_idss) - set(message_attachment_ids))
    #         attachmentObj = self.env['ir.attachment'].browse(ids)
    #         self.attachment_ids = attachmentObj
    #         return attachmentObj

    def action_create_proof(self):
        self.ensure_one()
        self.check_active_proof()
        if self.sale_line_id:
            proofing_obj = self.env['sale.tmg_proofing']
            proof = proofing_obj.create({
                'sale_line': self.sale_line_id.id,
                'art_file': self.art_file.id,
                'state': 'pending',
                'send_attachments': self.send_attachments,
                'email_ids': [(6,0,self.email_ids.ids)],
                'suggested_layout': self.suggested_layout


            })
            proof.send_proof()
        return {'type': 'ir.actions.act_window_close'}