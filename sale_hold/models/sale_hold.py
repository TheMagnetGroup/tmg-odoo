# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions


class sale_hold(models.Model):

    _name = 'sale.hold'
    _description = "Order Hold"
    name = fields.Char(string="Name")
    blocks_production = fields.Boolean(string="Blocks Production")
    blocks_delivery = fields.Boolean(string="Blocks Delivery")
    color = fields.Char(string="Color")
    active = fields.Boolean(string="Active")
    group_ids = fields.Many2many("res.groups", "rel_sales_to_holds", 'salesid', 'holdid',string="Security Group")
    credit_hold = fields.Boolean(string="Credit Hold")
    promostandards_hold_description = fields.Char(string="Promostandards Hold Description")
    sales_order_ids = fields.Many2many("sale.order", string = "Sales Orders")

    @api.multi
    def unlink(self):
        """Allows to delete sales order lines in draft,cancel states"""
        for rec in self:
            hasGroup = any([self.env.user.has_group(grp.id) for grp in rec.group_ids])
            if not hasGroup:
                raise exceptions.ValidationError(('Cannot delete hold due to security \'%s\'.') % (rec.state,))
        return super(SalesHold, self).unlink()

