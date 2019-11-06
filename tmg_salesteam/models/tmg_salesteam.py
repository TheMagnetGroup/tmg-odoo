# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class tmg_salesteam(models.Model):
    _inherit = 'crm.team'

    team_member_ids = fields.Many2many('res.users', 'team_member_id_rel', 'member_id', 'user_id', string='Channel Team Members', domain= lambda self: [('groups_id', 'in', self.env.ref('base.group_user').id)], help="Add members to the sales team.")

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # provide link to partner/contact "is customer" flag to condition salesteam in sales.view_order_form
    partner_is_customer = fields.Boolean('Is Customer', related='partner_id.customer')