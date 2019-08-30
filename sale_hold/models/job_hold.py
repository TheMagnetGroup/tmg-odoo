# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions
from odoo.exceptions import UserError

class JobHold(models.Model):
    _inherit = 'mrp.job'
    on_hold = fields.Boolean(string="On Hold")

    @api.multi
    def action_mark_as_done(self):
        if self.on_hold:
            raise UserError('This order has holds preventing processing.')

        ret = super(JobHold, self).action_mark_as_done()
        return ret

    @api.multi
    def action_reserve_all(self):
        if self.on_hold:
            raise UserError('This order has holds preventing processing.')

        ret = super(JobHold, self).action_reserve_all()
        return ret

    @api.multi
    def action_plan_all(self):
        if self.on_hold:
            raise UserError('This order has holds preventing processing.')

        ret = super(JobHold, self).action_plan_all()
        return ret



