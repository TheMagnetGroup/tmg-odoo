# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # this instruction "blanks-out" the Sales Team when Customer (i.e. partner_id) is blank
    # ... (e.g. when beginning CREATE() of a sales order)
    team_id = fields.Many2one(default=fields.Integer(0))


class tmg_salesteam(models.Model):
    _inherit = 'crm.team'

    team_member_ids = fields.Many2many('res.users', 'team_member_id_rel', 'member_id', 'user_id', string='Channel Team Members', domain= lambda self: [('groups_id', 'in', self.env.ref('base.group_user').id)], help="Add members to the sales team.")

