from odoo import models, fields, api
import json
import lxml.etree as le


class APILogging(models.Model):
    _name = 'tmg_external_api.api_logging'
    name = fields.Char(string="Display Name", store=True, readonly=True, compute="_get_order_name")
    api_name = fields.Char(string="API Name", required=True)
    partner_id = fields.Many2one("res.partner", string="Partner", required=True)
    request = fields.Text(string="Request")


    @api.depends('api_name', 'partner_id')
    def _get_order_name(self):
        name = self.api_name or ''
        partner_name = self.partner_id.name or ''
        self.name= partner_name + "," + name

    @api.depends('request')
    def _redact_password(self):
        val = self.request
        if val.contains('</'):
            doc = le.parse(val)
            for elem in doc.xpath('//password'):
                elem.text = ''

            self.request = le.tostring(doc)


