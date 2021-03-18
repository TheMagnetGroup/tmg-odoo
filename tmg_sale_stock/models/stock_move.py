# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class StockMove(models.Model):
    _inherit = 'stock.move'

    is_split_move = fields.Boolean('Is a Split Move',
                                   help='This is a technical field to detect if a move is a split move')

    @api.multi
    @api.depends('reserved_availablility')
    def _notify_backorder_picking(self):
        picking = self.picking_id
        if self.reserved_availability > 0:
            if picking:
                if picking.backorder_id:
                    self.action_send_notification(picking.backorder_id)
                    picking.backorder_id.sale_id.printed_date = ''

    @api.multi
    def action_send_notification(self, backorder_id):
        warehouse = backorder_id.location_id.warehouse_id
        if warehouse.backorder_channel:
            channel_id = warehouse.backorder_channel
            channel_id.message_post(subject='Backorder Inventory Reservation',
                                    body="The following backorder has an inventory reservation " + backorder_id,
                                    subtype='mail.mt_comment')
    # we need to pass the sale_line_id info for the sake of figuring out splitting
    def _prepare_procurement_values(self):
        res = super(StockMove, self)._prepare_procurement_values()
        res.update({'sale_line_id': self.sale_line_id.id})
        return res

    # we want to add the is_split_move_flag into the super
    # we also change the new move's partner_id when partner_id_int is passed in
    def _prepare_move_split_vals(self, qty):
        vals = super(StockMove, self)._prepare_move_split_vals(qty)
        # the good ole context trick
        if self.env.context.get('is_split_move_flag'):
            vals['is_split_move'] = True
            if self.env.context.get('partner_id_int'):
                vals['partner_id'] = self.env.context.get('partner_id_int')
        return vals

    # Modify the existing search picking method so that
    # partner and origin are take into consideration when it is a split move
    # this way we split stock.picking when the partner is different
    def _search_picking_for_assignation(self):
        self.ensure_one()
        if self.is_split_move:
            picking = self.env['stock.picking'].search([
                ('group_id', '=', self.group_id.id),
                ('location_id', '=', self.location_id.id),
                ('location_dest_id', '=', self.location_dest_id.id),
                ('picking_type_id', '=', self.picking_type_id.id),
                ('printed', '=', False),
                ('state', 'in', ['draft', 'confirmed', 'waiting', 'partially_available', 'assigned']),
                ('partner_id', '=', self.partner_id.id),
                ('origin', '=', self.origin)
            ], limit=1)
            return picking
        else:
            return super(StockMove, self)._search_picking_for_assignation()

    # new helper funtion to check if a move should be split
    def _check_if_move_should_be_split(self):
        self.ensure_one()
        # we don't want to split a move if it is already split
        # split when there is additional delivery addresses on SOL
        # or pretend this is a split move when other lines of the same order has split
        # the last logic is to make sure that non-split lines get treated and grouped the same way
        # in the picking process
        return (not self.is_split_move) \
               and self.sale_line_id \
               and any(self.sale_line_id.order_id.order_line.mapped('delivery_ids'))

    # the main helper funtion for this dev: this is to split a move before picking is assigned
    # The idea is we only want to split the move right before we know it is going to affect a picking
    # so that the manufacture order logic is intact
    def _split_move_before_assigning_picking(self):
        self.ensure_one()
        if self._check_if_move_should_be_split():
            # behold, we are splitting the move
            for delivery in self.sale_line_id.delivery_ids:
                # only split when there is qty
                # todo: use the float func instead to be safe
                if delivery.qty:
                    partner_id = delivery.shipping_partner_id
                    new_mid = self.with_context({
                        'is_split_move_flag': True,
                        'partner_id_int': partner_id.id
                    })._split(delivery.qty)
                    # if _split() didn't register due to complete split
                    # we force the partner_id to change
                    if new_mid == self.id:
                        self.partner_id = partner_id
            # after all splitting, our move is also a split move, yay
            # this is necessary so that recursion don't punish us later
            self.is_split_move = True

    def _assign_picking(self):
        # apply the split before assigning picking
        for move in self:
            move._split_move_before_assigning_picking()
        return super(StockMove, self)._assign_picking()

