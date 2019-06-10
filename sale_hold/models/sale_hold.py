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
        if context is None:
            context = {}
        """Allows to delete sales order lines in draft,cancel states"""
        hasGroup = False
        for rec in self.browse(cr, uid, ids, context=context):

            for grp in rec.group_ids:
                if self.env.user.has_group(rec.id):
                    hasGroup = True
            if not hasGroup:
                raise exceptions.except_osv(('Invalid Action!'),
                                            ('Cannot delete hold due to security \'%s\'.') % (rec.name,))
        return super(sale_hold, self).unlink()