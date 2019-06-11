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

    @api.multi
    def unlink(self):
        """Allows to delete sales order lines in draft,cancel states"""
        hasGroup = False
        for rec in self:
            for grp in rec.group_ids:
                rec_dic = grp.get_external_id()
                rec_list = list(rec_dic.values())
                rec_id = rec_list[0]
                if self.env.user.has_group(rec_id):
                    hasGroup = True
            if len(rec.group_ids)==0:
                hasGroup= True
            if not hasGroup:
                raise Warning('Cannot delete hold due to security ')
        return super(sale_hold, self).unlink()