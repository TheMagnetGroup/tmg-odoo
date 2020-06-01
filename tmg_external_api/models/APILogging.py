from odoo import models, fields, api
import json


class APILogging(models.Model):
    _name = 'tmg_external_api.api_logging'
    api_name = fields.Char(string="API Name")
    partner_id = fields.Many2one("res.partner", string="partner")
    request = fields.Text(string="Request")