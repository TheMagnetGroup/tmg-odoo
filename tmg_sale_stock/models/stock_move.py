# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _get_ups_service_types(self):
        return self.env['delivery.carrier']._get_ups_service_types()
    is_split_move = fields.Boolean('Is a Split Move',
                                   help='This is a technical field to detect if a move is a split move')


    carrier_id = fields.Many2one('delivery.carrier', string="Delivery Carrier")
    ups_carrier_account = fields.Char( string='Carrier Account', readonly=False)
    ups_service_type = fields.Selection(_get_ups_service_types, string="UPS Service Type")
    fedex_carrier_account = fields.Char(string='Fedex Carrier Account', readonly=False)
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
            if not self.carrier_id:
                ord = self.sale_line_id.order_id
                vals['carrier_id'] = self.env.context.get('carrier_id_int')
                # res.update({'carrier_id': ord.carrier_id})

                if ord.ups_service_type:
                    carrier = self.env['delivery.carrier'].browse(self.env.context.get('carrier_id'))
                    if carrier.delivery_type == 'ups' :
                        if self.env.context.get('ups_service_type'):

                            vals['ups_service_type'] = self.env.context.get('ups_service_type')
                        # res.update({'ups_service_type': ord.ups_service_type})
                        if ord.ups_carrier_account:
                            vals['ups_carrier_account'] = self.env.context.get('ups_carrier_account')
                    if carrier.delivery_type =='fedex':
                        if ord.fedex_carrier_account:
                            vals['fedex_carrier_account'] = self.env.context.get('fedex_carrier_account')
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
                        'partner_id_int': partner_id.id,
                        'carrier_id_int': delivery.carrier_id.id,
                        'ups_service_type': delivery.ups_service_type,
                        'ups_carrier_account': delivery.ups_carrier_account,
                        'fedex_carrier_account': delivery.fedex_carrier_account
                    })._split(delivery.qty)
                    # if _split() didn't register due to complete split
                    # we force the partner_id to change
                    if new_mid == self.id:
                        self.partner_id = partner_id
                        self.carrier_id = delivery.carrier_id.id
                        self.ups_service_type = delivery.ups_service_type
                        self.ups_carrier_account = delivery.ups_carrier_account
                        self.fedex_carrier_account = delivery.fedex_carrier_account
            # after all splitting, our move is also a split move, yay
            # this is necessary so that recursion don't punish us later
            self.is_split_move = True

    def _assign_picking(self):
        # apply the split before assigning picking
        for move in self:
            move._split_move_before_assigning_picking()
        return super(StockMove, self)._assign_picking()

    def _get_new_picking_values(self):

        vals = super(StockMove, self)._get_new_picking_values()
        vals['carrier_id'] = self.carrier_id.id
        vals['ups_service_type'] = self.ups_service_type
        vals['ups_carrier_account'] = self.ups_carrier_account
        vals['fedex_carrier_account'] = self.fedex_carrier_account
        # del(vals['carrier_id'])
        return vals

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        distinct_fields = super(StockMove, self)._prepare_merge_moves_distinct_fields()
        distinct_fields.append('carrier_id')
        distinct_fields.append('ups_service_type')
        distinct_fields.append('ups_carrier_account')
        distinct_fields.append('fedex_carrier_account')
        return distinct_fields

    @api.model
    def _prepare_merge_move_sort_method(self, move):
        move.ensure_one()
        keys_sorted = super(StockMove, self)._prepare_merge_move_sort_method(move)
        keys_sorted.append(move.sale_line_id.id)
        return keys_sorted

