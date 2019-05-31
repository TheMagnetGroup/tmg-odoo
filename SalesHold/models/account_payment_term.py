# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions

class AccountPaymentTerm(models.Model):
    _inherit = "account.payment.term"

    auto_credit_check = fields.Boolean(string="Automatic Credit Check", help="If this box is checked, an automatic credit check will be run when attempting to confirm a sale which uses this payment terms")
