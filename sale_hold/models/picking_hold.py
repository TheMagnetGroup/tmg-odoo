# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError

class picking_sales_hold(models.Model):
    _inherit = "stock.picking"

    on_hold = fields.Boolean(string="On Hold", related='sale_id.on_shipping_hold')
    on_hold_text = fields.Char(string="Hold Text")

    @api.multi
    @api.depends('on_hold')
    def update_on_change_text(self):
        if self.on_hold:
            self.on_hold_text = 'On Hold'
        else:
            self.on_hold_text = ''


    @api.multi
    def button_validate(self):
        for h in self.sale_id.order_holds:
            if h.blocks_delivery:
                raise UserError('This order has holds preventing shipping.')
        ret=super(picking_sales_hold,self).button_validate()
        return ret