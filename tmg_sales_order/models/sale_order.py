# -*- coding: utf-8 -*-

from odoo import models, fields, api


class tmg_sales_order(models.Model):
    _inherit = "sale.order"
    order_notes = fields.Text('Order Notes')

    @api.multi
    def action_view_mo_orders(self):
        '''
        This function returns an action that display existing delivery orders
        of given sales order ids. It can either be a in a list or in a form
        view, if there is only one delivery order to show.
        '''
        action = self.env.ref('mrp.mrp_production_action').read()[0]
        pickings = self.mapped('order_line')
        moves = pickings.mapped('move_ids')
        workorders = moves.mapped('created_production_id')



        action['domain'] = [('id', 'in', pickings.ids)]
        return action
