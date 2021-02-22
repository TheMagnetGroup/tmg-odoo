# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, Warning, UserError
from odoo.addons import decimal_precision as dp
from odoo.tools import float_compare, float_round
# from odoo.tools.profiler import profile
from odoo.tools.misc import profile


class SaleOrderLineDelivery(models.Model):
    _name = 'sale.order.line.delivery'
    _description = 'Specify delivery address on sale order line level.'

    sale_line_id = fields.Many2one('sale.order.line', ondelete='cascade', string='Sale Order Line')
    shipping_partner_id = fields.Many2one('res.partner', ondelete='cascade', string='Additional Delivery Address (SOL)', required=False)
    qty = fields.Float('Delivery Quantity', digits=dp.get_precision('Product Unit of Measure'))


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    delivery_ids = fields.One2many('sale.order.line.delivery', 'sale_line_id', string='Additional Deliveries (SOL)', copy=True)

    delivery_qty_sum = fields.Float('Delivery Qty Sum', compute='_compute_delivery_qty_sum', store=True,
                                    help='Technical field used to detect if delivery qty on SOL is exceeding current SOL qty',
                                    digits=dp.get_precision('Product Unit of Measure'))

    # make delivery_ids a protected field so that we don't mess it up after confirmation?
    def _get_protected_fields(self):
        res = super(SaleOrderLine, self)._get_protected_fields()
        res.extend(['delivery_ids'])
        return res

    @api.multi
    @api.depends('delivery_ids', 'delivery_ids.qty')
    def _compute_delivery_qty_sum(self):
        for sol in self:
            sol.delivery_qty_sum = sum(sol.delivery_ids.mapped('qty'))

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


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    delivery_update_ok = fields.Boolean('Can Update Delivery', help='technical field to make sure a delivery is updatable - meaning there is no confirmed delivery for this order.', compute="_compute_delivery_update_ok", store=True)

    @api.multi
    @api.depends('state', 'picking_ids', 'picking_ids.state')
    def _compute_delivery_update_ok(self):
        for order in self:
            if order.state == 'sale' and order.picking_ids and 'done' not in order.picking_ids.mapped('state'):
                order.delivery_update_ok = True
            else:
                order.delivery_update_ok = False

    # @api.multi
    # @profile('/home/cindey/debugModules/prof.profile')
    def action_update_delivery(self):
        for order in self:
            if not order.delivery_update_ok:
                raise ValidationError(_('Cannot update delivery when there is at least one confirmed delivery.'))
            # old_move_orig_ids = order.picking_ids.filtered(lambda pick: pick.picking_type_code == 'outgoing').mapped('move_ids_without_package.move_orig_ids.id')
            # old_production_ids = self.env['mrp.production'].search([('sale_line_id', 'in', order.order_line.ids)])
            #
            order.picking_ids.action_cancel()
            order.picking_ids.unlink()
            # order.order_line.with_context(ignore_assigned=True)._action_launch_stock_rule()
            #
            # if old_move_orig_ids and old_production_ids:
            #     new_move_ids = order.picking_ids.filtered(lambda pick: pick.picking_type_code == 'outgoing').mapped('move_ids_without_package.move_orig_ids')
            #     order.picking_ids.filtered(lambda pick: pick.picking_type_code == 'outgoing').mapped('move_ids_without_package').write({'move_orig_ids': [(6, 0, old_move_orig_ids)]})
            #
            #     new_production_ids = new_move_ids.mapped('production_id')
            #     # new_move_ids.unlink()
            #     new_production_ids.action_cancel()
            #     new_production_ids.unlink()
            #
            errors = []
            for line in order.order_line:
                values = line._prepare_procurement_values()
                quant_uom = line.product_id.uom_id
                get_param = self.env['ir.config_parameter'].sudo().get_param

                for delivery in line.delivery_ids:
                    procurement_uom = line.product_uom

                    group_id = self.env['procurement.group'].create({
                        'name': line.order_id.name, 'move_type': line.order_id.picking_policy,
                        'sale_id': line.order_id.id,
                        'partner_id': delivery.shipping_partner_id.id,
                    })

                    values.update({'partner_id': delivery.shipping_partner_id.id,
                                   'group_id': group_id})

                    product_qty = delivery.qty

                    if procurement_uom.id != quant_uom.id and get_param('stock.propagate_uom') != '1':
                        product_qty = line.product_uom._compute_quantity(product_qty, quant_uom,
                                                                         rounding_method='HALF-UP')
                        procurement_uom = quant_uom

                    try:
                        self.env['procurement.group'].run(line.product_id, product_qty, procurement_uom,
                                                          delivery.shipping_partner_id.property_stock_customer,
                                                          line.name, line.order_id.name, values)
                    except UserError as error:
                        errors.append(error.name)

            if errors:
                raise UserError('\n'.join(errors))

            #TODO: handle case with leftovers, put those in the main address

        return True
