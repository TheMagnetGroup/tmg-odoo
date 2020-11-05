# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    scheduled_date = fields.Datetime(string='Scheduled Date', store=True, related='picking_id.scheduled_date')


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    accounting_date = fields.Date(copy=False)

    
class InventoryLine(models.Model):
    _inherit = "stock.inventory.line"

    last_verified_uid = fields.Many2one(comodel_name='res.users', string='Last Verified By', copy=False)
    last_verified_date = fields.Datetime(string='Last Verified On', copy=False)

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


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _action_done(self):
        moves_todo = super(StockMove, self)._action_done()

        for move in moves_todo:
            # If the accounting date was specified on the adjustment then set the stock.move and
            # stock.move.line entries to the same date.
            if move.inventory_id.accounting_date:
                new_date = datetime.combine(move.inventory_id.accounting_date, datetime.max.time())
                move.write({'date': new_date})
                for move_line in move.move_line_ids:
                    move_line.write({'date': new_date})

        return moves_todo

