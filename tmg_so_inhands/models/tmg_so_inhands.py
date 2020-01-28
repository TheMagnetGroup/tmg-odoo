# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError
class tmg_so_inhands(models.Model):

    _inherit = "sale.order"
    in_hands = fields.Datetime(string="In-Hands Date")
    commitment_date = fields.Datetime('Ship Date',
                                      states={'draft': [('readonly', False)], 'sent': [('readonly', False)], 'sale': [('readonly', False)]},
                                      copy=False, oldname='requested_date', readonly=True,
                                      help="This is the delivery date promised to the customer. If set, the delivery order "
                                           "will be scheduled based on this date rather than product lead times.")

    @api.onchange('commitment_date')
    def _onchange_commitment_date(self):
        """ Warn if the commitment dates is sooner than the expected date """
        if (self.commitment_date and self.expected_date and self.commitment_date < self.expected_date):
            return {
                'warning': {
                    'title': _('Requested date is too soon.'),
                    'message': _("The ship date is sooner than the expected date."
                                 "You may be unable to honor the ship date.")
                }
            }

    @api.multi
    @api.onchange('commitment_date', 'in_hands')
    def onchange_in_hands_date(self):
        for order in self:
            if order.commitment_date and order.in_hands:
                if order.commitment_date > order.in_hands:
                    return {
                        'warning': {
                            'title': _('In Hands date is scheduled before ship date.'),
                            'message': _("The in hands date is sooner than the ship date. "
                                         "You may be unable to honor the in hands date.")
                        }
                    }
            if order.in_hands:
                if order.in_hands < datetime.today():
                    return {
                        'warning': {
                            'title': _('In hands date is before today. '),
                            'message': _("The in hands date is sooner than today."
                                         "Please select a valid in hands date.")
                        }
                    }
