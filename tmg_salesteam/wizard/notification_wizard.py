# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class NotificationWizardTmgSalesTeam(models.TransientModel):
    _name = 'notification.tmg.salesteam.wizard'
    _description = 'Notification Wizard'

    def get_default(self):
        if self.env.context.get("message", False):
            return self.env.context.get("message")
        return False

    name = fields.Text(string="Message", readonly=True, default=get_default)
