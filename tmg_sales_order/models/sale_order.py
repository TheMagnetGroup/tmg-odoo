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
        action['domain'] = [('sale_line_id.order_id', '=', self.id)]
        return action

  #  @api.onchange('order_line')
   # def _compute_production_orders(self):
    #    for order in self:
     #       orders = self.env['mrp.production'].search_count([
      #          ('sale_line_id.order_id', '=', self.id),
       #     ])

        #    order.production_orders_count = orders







