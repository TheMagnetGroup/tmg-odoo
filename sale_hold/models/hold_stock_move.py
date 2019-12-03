# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions
from odoo.exceptions import UserError

class hold_stock_move(models.Model):
    _inherit = 'stock.move'
    on_hold = fields.Boolean(string="On Hold")

    def _action_confirm(self, merge=True, merge_into=False):
        if self.on_hold:
            raise UserError('This order has holds preventing confirmation.')

        ret = super(hold_stock_move, self)._action_confirm()
        return ret