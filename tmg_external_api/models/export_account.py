# -*- coding: utf-8 -*-

from odoo import models, fields


class ExportAccount(models.Model):
    _name = 'tmg_external_api.tmg_export_account'
    _description = 'Export Accounts'

    category = fields.Char(string="Category")
    name = fields.Char(string="Name")
    accounting_id = fields.Char(string="Accounting ID")
    account_number = fields.Char(string="Account Number")
    login = fields.Char(string="Login")
    pwd = fields.Char(string="Password")
    url = fields.Char(string="Url")
    xslt_file = fields.Many2one(comodel_name="ir.attachment", string="XSLT File", ondelete="restrict")

    SAGERequest = {
        'Request': '',
        'APIVer': '210',
        'Auth': {
            'AcctID': '',
            'Token': '',
            'SAGENum': ''
        }
    }

    ASIAuth = {
        'Asi': '',
        'Username': '',
        'Password': ''
    }

    def get_sage_credentials(self, sage_request):
        request = self.SAGERequest
        # Set the request credentials from the model
        request['Request'] = sage_request
        request['Auth']['AcctID'] = self.accounting_id
        request['Auth']['Token'] = self.pwd
        request['Auth']['SAGENum'] = self.account_number

        return request

    def get_asi_credentials(self):
        request = self.ASIAuth
        # Set the request credentials from the model
        request['Asi'] = self.account_number
        request['Username'] = self.login
        request['Password'] = self.pwd

        return request
