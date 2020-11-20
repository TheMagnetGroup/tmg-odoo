from odoo import models, fields, api, exceptions
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

class Partner(models.Model):
    _inherit = "res.partner"

    promostandards = fields.Boolean(string="PromoStandards")
    daily_call_cap = fields.Integer(string="Daily Call Cap", default=9999)
    current_call_count = fields.Integer(string="Current Call Cap", default=0)
    debug = fields.Boolean(string = "Debug")
    technical_contact = fields.Many2one("res.partner", string="Technical Contact", ondelete='restrict')
    # Method to called by CRON to update SLA & statistics
    @api.model
    def reset_call_cap(self):
        partners = self.search(
            [('promostandards', '=', True)])
        for partner in partners:
            partner.write({'current_call_count': 0})

        return True

        # Method to called by CRON to update SLA & statistics

    @api.multi
    def check_cap(self):
        partners = self.search(
            [('promostandards', '=', True)])
        for partner in partners:
            partner.current_call_cap = 0

        return True