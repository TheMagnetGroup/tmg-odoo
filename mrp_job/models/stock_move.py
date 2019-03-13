# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _prepare_procurement_values(self):
        result = super(StockMove, self)._prepare_procurement_values()
        if self.sale_line_id:
            result['art_ref'] = self.sale_line_id.art_ref
        return result
