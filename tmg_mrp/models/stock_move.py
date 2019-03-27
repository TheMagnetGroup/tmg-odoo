# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

import logging
_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _prepare_procurement_values(self):
        res = super(StockMove, self)._prepare_procurement_values()
        res.update({'sale_line_id': self.sale_line_id.id})
        return res