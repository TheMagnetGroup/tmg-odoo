# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.addons import decimal_precision as dp


class tmg_available_to_sell(models.Model):
    _inherit = 'product.template'

    virtual_available_qty = fields.Float(
        'Available Quantity', search='_search_qty_available',
        digits=dp.get_precision('Product Unit of Measure'),
        help="Available Quantity (computed as Quantity On Hand "
             "- Outgoing)\n")


class _compute_quantities(models.Model):
    _inherit = 'product.product'

    @api.depends('stock_move_ids.product_qty', 'stock_move_ids.state')
    def _compute_quantities(self):
        super(_compute_quantities, self).create()
        for product in self:
            product.virtual_available_qty = product.qty_available-product.outgoing_qty