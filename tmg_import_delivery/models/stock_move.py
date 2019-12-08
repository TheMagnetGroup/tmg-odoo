from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class StockMove(models.Model):
    _inherit = 'stock.move'
    def _get_ups_service_types(self):
        return self.env['delivery.carrier']._get_ups_service_types()

    carrier_id = fields.Many2one('delivery.carrier', string="Delivery Carrier")
    ups_carrier_account = fields.Char( string='Carrier Account', readonly=False)
    ups_service_type = fields.Selection(_get_ups_service_types, string="UPS Service Type")
    fedex_carrier_account = fields.Char(string='Fedex Carrier Account', readonly=False)


    # def _prepare_procurement_values(self):
    #     res = super(StockMove, self)._prepare_procurement_values()
    #     if not self.carrier_id:
    #         ord = res.sale_line_id.order_id
    #         res.update({'carrier_id': ord.carrier_id})
    #         if ord.ups_service_type:
    #             res.update({'ups_service_type': ord.ups_service_type})
    #             if ord.ups_carrier_account:
    #                 res.update({'ups_carrier_account': ord.ups_carrier_account})
    #     return res

    # we want to add the is_split_move_flag into the super
    # we also change the new move's partner_id when partner_id_int is passed in
    def _prepare_move_split_vals(self, qty):
        vals = super(StockMove, self)._prepare_move_split_vals(qty)
        # the good ole context trick
        if self.env.context.get('is_split_move_flag'):
            ord = self.sale_line_id.order_id
            vals['is_split_move'] = True
            if self.env.context.get('scheduled_date'):
                vals['scheduled_date'] = self.env.context.get('scheduled_date')
            else:
                vals['scheduled_date'] = ord.commitment_date
            if not self.carrier_id:

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
                        # res.update({'ups_carrier_account': ord.ups_carrier_account})
        return vals



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
                        'carrier_id_int' : delivery.carrier_id.id,
                        'ups_service_type' : delivery.ups_service_type,
                        'ups_carrier_account' : delivery.ups_carrier_account,
                        'fedex_carrier_account' : delivery.fedex_carrier_account,
                        'scheduled_date' : delivery.scheduled_date
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

