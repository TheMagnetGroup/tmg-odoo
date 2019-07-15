# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

import logging
_logger = logging.getLogger(__name__)


class StockRule(models.Model):
    _inherit = 'stock.rule'

    """
    Why do we overwrite _prepare_mo_vals() here?
    
    sale.order -> action_confirm() -> _action_confirm()
    sale.order.line -> _action_launch_stock_rule() -> _prepare_procurement_values(group_id)  # 'group id' is procurement group
    procurement.group -> run()  # if it is mto -> 
    stock.rule -> _run_manufacture() -> prepare_mo_vals(values)     
    """
    def _prepare_mo_vals(self, product_id, product_qty, product_uom, location_id, name, origin, values, bom):
        res = super(StockRule, self)._prepare_mo_vals(product_id, product_qty, product_uom, location_id, name, origin, values, bom)
        res.update({'sale_line_id': values.get('sale_line_id', False)})  # sale_line_id info is in values, we just need to pass it
        return res


# For debug purpose
# class ProcurementGroup(models.Model):
#     _inherit = 'procurement.group'
#
#     @api.model
#     def run(self, product_id, product_qty, product_uom, location_id, name, origin, values):
#         res = super(ProcurementGroup, self).run(product_id, product_qty, product_uom, location_id, name, origin, values)
#         return res