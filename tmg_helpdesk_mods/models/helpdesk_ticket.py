    # -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, date, timedelta


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    # Method to called by CRON to update SLA & statistics
    @api.model
    def tmg_check_sla(self):
        tickets = self.search([('stage_id.is_close', '=', False),('sla_id','!=',False),('team_id.name','=','Urgent')])
        urgent_channel = self.env['mail.channel'].search([('name', '=', 'urgent')])
        for ticket in tickets:
            if ticket.stage_id.sequence < ticket.sla_id.stage_id.sequence and fields.datetime.now() > ticket.deadline:
                if urgent_channel:
                    ticket.message_subscribe(channel_ids=[urgent_channel.id])
                    urgent_channel.message_post(body=_('Urgent ticket %s was not assigned according to SLA!') % ticket.name, message_type='comment', subtype='mail.mt_comment')

        return True

    # Method to change Ticket Status to Assigned when Tech is added
    @api.model
    def create(self, vals):
        if vals.get('user_id'):
            vals['stage_id'] = 2
        return super(HelpdeskTicket, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('user_id'):
            vals['stage_id'] = 2
        return super(HelpdeskTicket, self).write(vals)







