# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions
from odoo.exceptions import UserError

class JobHold(models.Model):
    _inherit = 'mrp.production'
    on_hold = fields.Boolean(string="On Hold")


    @api.multi
    def open_produce_product(self):
        if self.on_hold:
            raise UserError('This order has holds preventing shipping.')

        ret = super(JobHold, self).button_validate()
        return ret