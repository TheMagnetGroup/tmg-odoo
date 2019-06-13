# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class TMG_StockPickingBatch(models.Model):
    _inherit = 'tock.picking.batch'
    _name = 'tmg_stock.picking.batch'

    @api.multi
    def print_picking(self):
        pickings = self.mapped('picking_ids')
        if not pickings:
            raise UserError(_('Nothing to print.'))
        return self.env.ref('tmg_stock_picking_batch.action_tmg_report_picking_batch').report_action(self)