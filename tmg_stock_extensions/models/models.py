# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    scheduled_date = fields.Datetime(string='Scheduled Date', store=True, related='picking_id.scheduled_date')

class InventoryLine(models.Model):
    _inherit = "stock.inventory.line"

    last_verified_uid = fields.Many2one(comodel_name='res.users', string='Last Verified By')
    last_verified_date = fields.Datetime(string='Last Verified On')

    @api.multi
    def verify(self):
        for sil in self:
            self.write({
                'last_verified_uid': self.env.user.id,
                'last_verified_date': datetime.today()
            })

    @api.multi
    def write(self, vals):
        vals['last_verified_uid'] = self.env.user.id
        vals['last_verified_date'] = datetime.today()
        res = super(InventoryLine, self).write(vals)
        self._check_no_duplicate_line()
        return res

    def _generate_moves(self):
        res = super(InventoryLine, self)._generate_moves()
        for move in res:
            if move.inventory_id.accounting_date:
                super().write({'date': datetime.combine(move.inventory_id.accounting_date, datetime.min.time())})
        return res

