# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions
from odoo.exceptions import AccessError, UserError, RedirectWarning, \
    ValidationError, Warning
class AccountPaymentTerm(models.Model):
    _inherit = "account.payment.term"

    auto_credit_check = fields.Boolean(string="Automatic Credit Check", help="If this box is checked, an automatic credit check will be run when attempting to confirm a sale which uses this payment terms")
    default_credit_terms = fields.Boolean(string="Default Credit Term", help="If this box is checked, this will be the credit term used by default when creating new accounts.")
    default_credit_limit = fields.Integer(string = "Default Credit Limit", help="Default credit limit to be used to default accounts receiving default credit terms.")

    @api.constrains('default_credit_limit')
    def check_credit_limit(self):
        for record in self:
            if record.default_credit_terms:
                if record.default_credit_limit== False or record.default_credit_limit == 0:
                    raise Warning("The default credit limit cannot be zero for the default credit term.")

    @api.constrains('auto_credit_check')
    def check_credit_terms(self):
        for record in self:
            if record.default_credit_terms:
                if record.auto_credit_check == False:
                    raise Warning("Auto Credit Check required for default.")

    @api.onchange('default_credit_terms')
    def _update_credit_check(self):
        if self.default_credit_terms:
            self.auto_credit_check = True
            if self.default_credit_limit== False or self.default_credit_limit == 0:
                self.default_credit_limit = 1


    @api.constrains('default_credit_terms')
    def _check_for_unique(self):
        terms = self.env['account.payment.term']
        default_terms = terms.search([('default_credit_terms', '=', True)])
        if len(default_terms) > 1:
            raise Warning("Cannot have more than one default credit term.")