# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, Warning
from odoo.addons import decimal_precision as dp


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # what happens when you confirm a sale order?
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        return res


class SaleOrderLineDelivery(models.Model):
    _name = 'sale.order.line.delivery'
    _description = 'Specify delivery address on sale order line level.'

    sale_line_id = fields.Many2one('sale.order.line', ondelete='cascade', string='Sale Order Line')
    shipping_partner_id = fields.Many2one('res.partner', string='Delivery Address (SOL)', required=True)
    qty = fields.Float('Delivery Qty', digits=dp.get_precision('Product Unit of Measure'))

    name = fields.Char(readonly=True, compute='_compute_default_name')

    @api.multi
    @api.depends('shipping_partner_id', 'shipping_partner_id.name', 'qty')
    def _compute_default_name(self):
        for sold in self:
            sold.name = '{}({})'.format(sold.shipping_partner_id.name, str(sold.qty))


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    delivery_ids = fields.One2many('sale.order.line.delivery', 'sale_line_id', string='Deliveries (SOL)', copy=True)

    delivery_qty_sum = fields.Float('Delivery Qty Sum', compute='_compute_delivery_qty_sum', store=True,
                                    help='Technical field used to detect if delivery qty on SOL is exceeding current SOL qty',
                                    digits=dp.get_precision('Product Unit of Measure'))

    @api.multi
    @api.depends('delivery_ids', 'delivery_ids.qty')
    def _compute_delivery_qty_sum(self):
        for sol in self:
            sol.delivery_qty_sum = sum(sol.delivery_ids.mapped('qty'))

    @api.multi
    @api.onchange('product_uom_qty', 'delivery_qty_sum')
    def _onchange_delivery_qty_sum(self):
        self.ensure_one()
        if self.product_uom_qty < self.delivery_qty_sum:
            self.product_uom_qty = self.delivery_qty_sum
            warning = {
                'title': _('More Qty to delivery addresses than were ordered'),
                'message': _('You have allocated more quantity to delivery addresses than were ordered. '
                             'The ordered quantity has been increased. '
                             'To decrease the ordered quantity, unallocate items from their delivery addresses.')
            }
            return {'warning': warning}
        elif self.delivery_qty_sum and self.product_uom_qty > self.delivery_qty_sum:
            warning = {
                'title': _('Less Qty to delivery addresses than were ordered'),
                'message': _('You have allocated less quantity to delivery addresses than were orders. '
                             'The remaining units have been allocated to the order\'s shipping address.')
            }
            return {'warning': warning}


