# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.addons import decimal_precision as dp


class tmg_available_to_sell(models.Model):
    _inherit = 'product.template'
    virtual_available_qty = fields.Float(
        'Available Quantity', search='_search_virtual_available_qty',
        digits=dp.get_precision('Product Unit of Measure'), compute='_compute_quantities',
        help="Available Quantity (computed as Quantity On Hand "
             "- Outgoing)\n")

    def _compute_quantities(self):
        res = super(tmg_available_to_sell, self)._compute_quantities()
        for template in self:
            template.virtual_available_qty = template.qty_available - template.outgoing_qty


class _compute_quantities(models.Model):
    _inherit = 'product.product'
    virtual_available_qty = fields.Float(
        'Available Quantity', search='_search_virtual_available_qty',
        digits=dp.get_precision('Product Unit of Measure'), compute='_compute_quantities',
        help="Available Quantity (computed as Quantity On Hand "
             "- Outgoing)\n")

    @api.depends('stock_move_ids.product_qty', 'stock_move_ids.state')
    def _compute_quantities(self):
        super(_compute_quantities, self)._compute_quantities()
        for product in self:
            product.virtual_available = product.qty_available - product.outgoing_qty
