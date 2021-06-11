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
    art_file = fields.Many2one("ir.attachment", string="ArtFiles", domain="[('id','in',[sale_order.attachment_ids]),('res_model', '=', 'sale.order')]")

    # @api.constrains('ups_service_type')
    # def _validate_account(self):
    #     if self.ups_service_type:
    #         if not self.ups_carrier_id and self.ups_bill_my_account:
    #             raise ValidationError("You cannot select a third party shipper without supplying an account number")

    def check_active_proof(self):
        proofs = any(l.state == 'pending' for l in self.sale_line_id.proofing_lines)

        if proofs:
            raise UserError('Please resolve pending proofs before creating new ones.')


    def action_create_proof(self):
        self.ensure_one()
        self.check_active_proof()
        if self.sale_line_id:



            proofing_obj = self.env['sale.tmg_proofing']
            proof = proofing_obj.create({
                'sale_line': self.sale_line_id.id,

                'art_file': self.art_file.id,
                'state': 'pending',

            })
            proof.send_proof()
        return {'type': 'ir.actions.act_window_close'}