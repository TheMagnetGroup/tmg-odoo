# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.tools import float_compare


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _check_routing(self):
        super(SaleOrderLine, self)._check_routing()
        return False

    @api.onchange('product_uom_qty', 'product_uom', 'route_id')
    def _onchange_product_id_check_availability(self):
        if not self.product_id or not self.product_uom_qty or not self.product_uom:
            self.product_packaging = False
            return {}
        if self.product_id.type == 'product':
            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            product = self.product_id.with_context(
                warehouse=self.order_id.warehouse_id.id,
                lang=self.order_id.partner_id.lang or self.env.user.lang or 'en_US'
            )
            product_qty = self.product_uom._compute_quantity(self.product_uom_qty, self.product_id.uom_id)
            check_qty = 0
            if self.order_id.warehouse_id.manufacture_to_resupply:
                check_qty = product.virtual_available_qty
            else:
                check_qty = product.virtual_available
            if float_compare(check_qty, product_qty, precision_digits=precision) == -1:
                is_available = self._check_routing()
                if not is_available:
                    message = _('You plan to sell %s %s of %s but you only have %s %s available in %s warehouse.') % \
                            (self.product_uom_qty, self.product_uom.name, self.product_id.name, check_qty, product.uom_id.name, self.order_id.warehouse_id.name)
                    # We check if some products are available in other warehouses.
                    check_all_qty = 0
                    if self.order_id.warehouse_id.manufacture_to_resupply:
                        check_all_qty = self.product_id.virtual_available_qty
                    else:
                        check_all_qty = self.product_id.virtual_available
                    if float_compare(check_qty, check_all_qty, precision_digits=precision) == -1:
                        message += _('\nThere are %s %s available across all warehouses.\n\n') % \
                                (check_all_qty, product.uom_id.name)
                        for warehouse in self.env['stock.warehouse'].search([]):
                            quantity = 0
                            if self.order_id.warehouse_id.manufacture_to_resupply:
                                quantity = self.product_id.with_context(warehouse=warehouse.id).virtual_available_qty
                            else:
                                quantity = self.product_id.with_context(warehouse=warehouse.id).virtual_available
                            if quantity > 0:
                                message += "%s: %s %s\n" % (warehouse.name, quantity, self.product_id.uom_id.name)
                    warning_mess = {
                        'title': _('Not enough inventory!'),
                        'message' : message
                    }
                    return {'warning': warning_mess}
        return {}