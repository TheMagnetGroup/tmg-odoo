# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, Warning
from odoo.addons import decimal_precision as dp
from odoo.tools import float_compare, float_round


class SaleOrderLineDelivery(models.Model):
    _name = 'sale.order.line.delivery'
    _description = 'Specify delivery address on sale order line level.'

    sale_line_id = fields.Many2one('sale.order.line', ondelete='cascade', string='Sale Order Line')
    shipping_partner_id = fields.Many2one('res.partner', ondelete='cascade', string='Additional Delivery Address (SOL)', required=False)
    qty = fields.Float('Delivery Quantity', digits=dp.get_precision('Product Unit of Measure'))

    # # todo: not necessary
    # name = fields.Char(readonly=True, compute='_compute_default_name')
    #
    # @api.multi
    # @api.depends('shipping_partner_id', 'shipping_partner_id.name', 'qty')
    # def _compute_default_name(self):
    #     for sold in self:
    #         sold.name = '{}({})'.format(sold.shipping_partner_id.name, str(sold.qty))


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # xname = fields.Char('External ID', compute='_compute_sale_line_xname', store=False)
    delivery_ids = fields.One2many('sale.order.line.delivery', 'sale_line_id', string='Additional Deliveries (SOL)', copy=True)

    delivery_qty_sum = fields.Float('Delivery Qty Sum', compute='_compute_delivery_qty_sum', store=True,
                                    help='Technical field used to detect if delivery qty on SOL is exceeding current SOL qty',
                                    digits=dp.get_precision('Product Unit of Measure'))

    # make delivery_ids a protected field so that we don't mess it up after confirmation?
    def _get_protected_fields(self):
        res = super(SaleOrderLine, self)._get_protected_fields()
        res.extend(['delivery_ids'])
        return res

    # @api.multi
    # def _compute_sale_line_xname(self):
    #     for sol in self:
    #         xid = self.env['ir.model.data'].sudo().search([('model', '=', 'sale.order.line'), ('res_id', '=', sol.id)], limit=1)
    #         if xid:
    #             sol.xname = xid.complete_name

    @api.multi
    @api.depends('delivery_ids', 'delivery_ids.qty')
    def _compute_delivery_qty_sum(self):
        for sol in self:
            sol.delivery_qty_sum = sum(sol.delivery_ids.mapped('qty'))

    # @api.model
    # def create(self, values):
    #     sols = super(SaleOrderLine, self).create(values)
    #     # force create xml ids
    #     # this crazy syntax is to call the hidden func from base model
    #     SaleOrderLine._BaseModel__ensure_xml_id(sols)
    #     return sols

    # inherit the private _write here to capture the value change in depends
    @api.multi
    def _write(self, values):
        res = super(SaleOrderLine, self)._write(values)
        if values.get('product_uom_qty') or values.get('delivery_qty_sum'):
            for sol in self:
                if sol.product_uom_qty < sol.delivery_qty_sum:
                    sol.product_uom_qty = sol.delivery_qty_sum
        return res

    # # we try to make the tree view an action here
    # @api.multi
    # def action_view_sale_line_delivery_tree(self):
    #     self.ensure_one()
    #     # force creating xml_id if there isn't any
    #     return {
    #         'name': _('SOL Additional Delivery Addresses'),
    #         'view_mode': 'tree',
    #         'target': 'self',
    #         'res_model': 'sale.order.line.delivery',
    #         'type': 'ir.actions.act_window',
    #         'domain': [('id', 'in', self.delivery_ids.mapped('id'))],
    #         'context': {'default_sale_line_id': self.id}
    #         }

    # onchange is too annoying for now, muted it
    # @api.multi
    # @api.onchange('product_uom_qty', 'delivery_qty_sum')
    # def _onchange_delivery_qty_sum(self):
    #     self.ensure_one()
    #     if self.product_uom_qty < self.delivery_qty_sum:
    #         self.product_uom_qty = self.delivery_qty_sum
    #         warning = {
    #             'title': _('More Qty to delivery addresses than were ordered'),
    #             'message': _('You have allocated more quantity to delivery addresses than were ordered. '
    #                          'The ordered quantity has been increased. '
    #                          'To decrease the ordered quantity, unallocate items from their delivery addresses.')
    #         }
    #         return {'warning': warning}
    #     elif self.delivery_qty_sum and self.product_uom_qty > self.delivery_qty_sum:
    #         warning = {
    #             'title': _('Less Qty to delivery addresses than were ordered'),
    #             'message': _('You have allocated less quantity to delivery addresses than were orders. '
    #                          'The remaining units have been allocated to the order\'s shipping address.')
    #         }
    #         return {'warning': warning}

    def action_unlink_all_additional_delivery_addresses(self):
        self.ensure_one()
        self.delivery_ids.unlink()

