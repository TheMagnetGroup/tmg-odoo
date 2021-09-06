# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError


class MassSalesTeamUpdate(models.TransientModel):
    _name = 'contact.sales.team.update.wizard'
    _description = 'Mass sales team update'

    team_id = fields.Many2one('crm.team', string='Sales Team')

    @api.multi
    def action_validate(self):
        if self.team_id:
            partner_ids = self.env['res.partner'].browse(self.env.context.get('active_ids', []))
            partner_ids and partner_ids.write({'team_id': self.team_id.id})
        else:
            raise UserError("Please select the sales team")
