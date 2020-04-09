# -*- coding: utf-8 -*-

from odoo import models, fields
from odoo.tools.misc import format_date


class Company(models.Model):
    _inherit = 'res.company'

    remit_to_id = fields.Many2one('res.partner', string='Remit To', required=False)


class AccountPayment(models.Model):
    _inherit = "account.payment"

    def _check_make_stub_line(self, invoice):
        """ Add invoice date to the stub line
        """
        tmg_stub_line = super(AccountPayment, self)._check_make_stub_line(invoice)

        tmg_stub_line['invoice_date'] = format_date(self.env, invoice.date_invoice)
        return tmg_stub_line
