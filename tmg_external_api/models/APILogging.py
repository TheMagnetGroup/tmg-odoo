from odoo import models, fields, api
import json


class APILogging(models.Model):
    _name = 'tmg_external_api.api_logging'
    name = fields.Char(string="Display Name", store=True, readonly=True, compute="_get_order_name")
    api_name = fields.Char(string="API Name", required=True)
    partner_id = fields.Many2one("res.partner", string="partner", required=True)
    request = fields.Text(string="Request")


    @api.depends('api_name', 'partner_id', 'name')
    def _get_order_name(self):
        self.name= self.api_name + "," + self.partner_id.name