# -*- coding: utf-8 -*-

from odoo import models, fields, api
import urllib.request
import json
import traceback

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
    file_extension = fields.Char(string="File Extension")
    export_account_ids = fields.One2many(comodel_name='product.export.account',
                                          inverse_name='export_account_id')
    folder = fields.Char(string="Folder")

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Export account name already exists!"),
    ]

    SAGERequest = {
        'Request': '',
        'APIVer': 210,
        'Auth': {
            'AcctID': '',
            'Token': '',
        },
        'SAGENum': 0
    }

    SAGEDiscontinueRequest = {
        "Products" : [
            {
                'UpdateType' : 0,
                'RefNum' : '',
                'ProductID' : 0,
                'SuppID' : 0,
                'ItemNum' : '',
                'Discontinued' : 1
            }
        ]
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
        request['SAGENum'] = self.account_number

        return request

    def get_asi_credentials(self):
        request = self.ASIAuth
        # Set the request credentials from the model
        request['Asi'] = self.account_number
        request['Username'] = self.login
        request['Password'] = self.pwd

        return request

    @api.model
    def check_sage_products(self, export_account):

        # We'll create a list of items discontinued via this routine
        discontinued_items = {}
        any_failure = False

        # Get the record for the passed account
        sage = self.search([('name', '=', export_account)])
        if sage:
            # Build the SAGE credentials structure
            sage_cred = sage.get_sage_credentials("ProductDataDownload")
            # Now cal the api to get the list of products from SAGE
            sagerequest = urllib.request.Request(sage.url,
                                             data=json.dumps(sage_cred).encode('utf-8'),
                                             method='POST')

            with urllib.request.urlopen(sagerequest) as sageresponse:
                # Read the entire response
                sageresponsestr = sageresponse.read().decode('utf-8')
                # Serialize the response into python. If unable to serialize then break out of the function
                try:
                    sageresponsedict = json.loads(sageresponsestr)
                except:
                    return

                # Now get the list of saleable products
                products = self.env['product.template'].get_product_saleable()
                products_style = products.mapped('product_style_number')

                # Go through each product in the SAGE response.  If not found in the current list of saleable
                # products then we need to discontinue the product in SAGE
                for product in sageresponsedict['Products']:
                    if product['ItemNum'] not in products_style:
                        sage_json_data = {}
                        # Create the basic request
                        sage_auth = sage.get_sage_credentials("ProductDataUpdate")
                        # Build the complete request, adding in the Json to discontinue the product
                        sage_json_data.update(sage_auth)
                        sage_json_data.update(self.SAGEDiscontinueRequest)
                        sage_json_data['Products'][0]['SuppID'] = sage.account_number
                        sage_json_data['Products'][0]['ItemNum'] = product['ItemNum']
                        # Send the product update to SAGE. NOTE: you must be VERY careful with the discontinue
                        # code. SAGE does not have a test environment so any discontinue requests will hit their LIVE
                        # database.
                        sage_disc_request = urllib.request.Request(sage.url,
                                                             data=json.dumps(sage_json_data).encode('utf-8'),
                                                             method='POST')
                        # General catch all
                        try:
                            with urllib.request.urlopen(sage_disc_request) as sage_disc_response:
                                # Read the entire response
                                sage_disc_responsestr = sage_disc_response.read().decode('utf-8')
                                # Serialize the response into python. If unable to serialize then break out of the function
                                try:
                                    sage_disc_responsedict = json.loads(sage_disc_responsestr)
                                except:
                                    any_failure = True
                                    discontinued_items[product['ItemNum']] = "Error serializing SAGE response: " + sage_disc_responsestr
                        except Exception as e:
                            any_failure = True
                            discontinued_items[product['ItemNum']] = "An exception occurred discontinuing the SAGE product: {0}".format(traceback.format_exc())

                        # If the response was NOT ok then set an error
                        if sage_disc_responsedict['Responses'][0]['OK'] == "0":
                            any_failure = True
                            discontinued_items[product['ItemNum']] = sage_disc_responsedict['Responses'][0]['Errors']
                        else:
                            discontinued_items[product['ItemNum']] = "OK"

                # If there was any failure send a helpdesk email with the attached dictionary
                if any_failure:

                    mail_body = ""
                    for item, message in discontinued_items.items():
                        mail_body += item + ": " + message + "\r\n"
                    mail = self.env['mail.mail']

                    values = {
                        'model': None,
                        'res_id': None,
                        'subject': 'SAGE Cross Check Failure for ' + export_account,
                        'body': mail_body,
                        'body_html': mail_body,
                        'email_from': 'noreply@themagnetgroup.com',
                        'email_to': 'ithelp@magnetllc.com'
                    }
                    mail.create(values).send()


class ProductExportAccount(models.Model):
    _name = 'product.export.account'
    _description = 'Product Export Account'

    name = fields.Char(string='Name')
    product_tmpl_id = fields.Many2one(comodel_name='product.template', string='Product Template', ondelete='restrict',
                                      required=True)
    export_account_id = fields.Many2one(comodel_name='tmg_external_api.tmg_export_account', string='Export Account',
                                        ondelete='restrict', required=True)
    export_product_data = fields.Boolean(string='Export Data', default=True)
    last_export_date = fields.Date(string='Last Export Date')
    last_export_error = fields.Boolean(string='Last Export Error')
    last_export_message = fields.Char(string='Last Export Error Message')


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    export_account_ids = fields.One2many(comodel_name='product.export.account', inverse_name='product_tmpl_id')