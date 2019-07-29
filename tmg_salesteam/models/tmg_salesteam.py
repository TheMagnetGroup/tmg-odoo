# -*- coding: utf-8 -*-

from odoo import models, fields, api

class tmg_salesteam(models.Model):
    _inherit = 'crm.team'

    member_ids = fields.Many2many('res.users', 'team_member_id_rel', 'member_id', 'user_id', string='Channel Members', domain= lambda self: [('groups_id', 'in', self.env.ref('base.group_user').id)], help="Add members to automatically assign their documents to this sales team.")

class tmg_user(models.Model):
    _inherit = 'res.users'

    sale_team_id = fields.Char(string='Overridden to disable functionality')