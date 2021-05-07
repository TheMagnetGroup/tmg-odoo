# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    quick_ship = fields.Boolean("Quick Ship Order")

    @api.multi
    @api.depends('order_line.quick_ship')
    def _compute_quick_ship(self):
        for record in self:
            if any(l.quick_ship and l.product_uom_qty > l.qty_invoiced for l in record.order_line):
                record.quick_ship = True
            else:
                record.quick_ship = False


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    decoration_method = fields.Char('Decoration Method', compute='_get_deco_method', store=True, help='Decoration method used on the sale order line')
    quick_ship = fields.Boolean("Quick Ship", copy=False)
    # printed_date = fields.Datetime(string="Date")
    @api.multi
    @api.depends('product_no_variant_attribute_value_ids')
    def _get_deco_method(self):
        """ Calculate the decoration method for this sale order line
            * decoration_method - stores the decoration method used on the order line
        """

        for line in self:
            for attribute in line.product_no_variant_attribute_value_ids:
                if attribute.attribute_id.name.strip() == "Decoration Method":
                    line.decoration_method = attribute.name

