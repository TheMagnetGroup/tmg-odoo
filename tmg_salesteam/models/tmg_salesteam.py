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

    @api.multi
    def name_get(self):
        result = []
        for team in self:
            result.append((team.id, "%s (%s)" % (team.name, team.user_id.name if team.user_id.name else "N/A")))
        return result


class tmg_team_users(models.Model):
    _inherit = 'res.users'

    user_team_ids = fields.Many2many('crm.team', 'team_member_id_rel', 'user_id', 'member_id', string='User Teams')


class ResPartnerTmgSalesteam(models.Model):
    _inherit = 'res.partner'

    team_id = fields.Many2one(track_visibility='onchange')

    @api.multi
    def action_update_sales_team(self):
        if not self.env.user.has_group('sales_team.group_sale_manager'):
            view = self.env.ref('tmg_salesteam.notification_wizard_form_view')
            view_id = view and view.id or False
            context = dict(self._context) or {}
            context.update({'message': 'You do not have the permission to execute this action.'})
            return {
                'name': 'Access denied',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'notification.tmg.salesteam.wizard',
                'views': [(view_id, 'form')],
                'view_id': view_id,
                'target': 'new',
                'context': context,
            }
        for rec in self:
            view = self.env.ref('tmg_salesteam.mass_sales_team_update_wizard_form_view')
            view_id = view and view.id or False
            context = dict(self._context) or {}
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'contact.sales.team.update.wizard',
                'views': [(view_id, 'form')],
                'view_id': view_id,
                'target': 'new',
                'context': context,
            }
