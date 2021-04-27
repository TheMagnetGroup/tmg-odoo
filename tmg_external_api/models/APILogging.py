from odoo import models, fields, api
import json
import lxml.etree as le
import re

class APILogging(models.Model):
    _name = 'tmg_external_api.api_logging'
    name = fields.Char(string="Display Name", store=True, readonly=True, compute="_get_order_name")
    api_name = fields.Char(string="API Name", required=True)
    partner_id = fields.Many2one("res.partner", string="Partner", required=True)
    request = fields.Text(string="Request")


    @api.depends('api_name', 'partner_id')
    def _get_order_name(self):
        for record in self:
            name = record.api_name or ''
            partner_name = record.partner_id.name or ''
            record.name = partner_name + "," + name

    @api.multi
    def write(self, vals):
        for record in self:
            if vals.get('request'):
                data = vals.get('request')
                data = self._redact_password(data)
                vals['request'] = data
            res = super(APILogging, self).write(vals)

    @api.model
    def create(self, vals):
        if vals.get('request'):
            request = vals.get('request')
            if 'xml' in request:
                data = self._redact_password(request)
                vals['request'] = data
        return super(APILogging, self).create(vals)

    def _redact_password(self, val):

        if '>' in val:
            val = re.sub(' xmlns="[^"]+"', '', val)
            # val = re.sub(' xsd="[^"]+"', '', val, count=1)
            # val = re.sub(' xsi="[^"]+"', '', val, count=1)
            doc = le.fromstring(val)

            for elem in doc.xpath('//password'):
                elem.text = ''



            return le.tostring(doc)
        return val


