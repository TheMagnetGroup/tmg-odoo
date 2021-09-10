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
    image_folder = fields.Char(string="Image Folder")
    company_id = fields.Many2one(comodel_name="res.company", string="Company")

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

    @api.multi
    def _sage_product_deactivation(self, export_account=''):
        # Get the record for the passed account
        export_account_ids = self.search([('name', '=', export_account)])
        for export_account_id in export_account_ids:
            # Build the SAGE credentials structure
            sage_cred = export_account_id.get_sage_credentials("ProductDataDownload")
            # Now cal the api to get the list of products from SAGE
            sagerequest = urllib.request.Request(export_account_id.url, data=json.dumps(sage_cred).encode('utf-8'),
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
                products = self.env['product.template'].with_context(
                    sage_product_check=True, company=export_account_id.company_id).get_product_saleable()
                products_style = products.mapped('product_style_number')

                # Go through each product in the SAGE response.  If not found in the current list of saleable
                # products then we need to discontinue the product in SAGE
                for product in sageresponsedict['Products']:
                    if product['ItemNum'] not in products_style:
                        product_id = self.env['product.template'].search(
                            [('product_style_number', '=', product['ItemNum'])], limit=1)
                        sage_json_data = {}
                        # Create the basic request
                        sage_auth = export_account_id.get_sage_credentials("ProductDataUpdate")
                        # Build the complete request, adding in the Json to discontinue the product
                        sage_json_data.update(sage_auth)
                        sage_json_data.update(self.SAGEDiscontinueRequest)
                        sage_json_data['Products'][0]['SuppID'] = export_account_id.account_number
                        sage_json_data['Products'][0]['ItemNum'] = product['ItemNum']
                        sage_json_data['Products'][0]['RefNum'] = product['ItemNum']
                        # Send the product update to SAGE. NOTE: you must be VERY careful with the discontinue
                        # code. SAGE does not have a test environment so any discontinue requests will hit their LIVE
                        # database.
                        sage_disc_request = urllib.request.Request(export_account_id.url,
                                                                   data=json.dumps(sage_json_data).encode('utf-8'),
                                                                   method='POST')

                        error_message = 'Sage discontinue request was failed'
                        success_message = ''

                        # General catch all
                        try:
                            with urllib.request.urlopen(sage_disc_request) as sage_disc_response:
                                # Read the entire response
                                sage_disc_responsestr = sage_disc_response.read().decode('utf-8')
                                # Serialize the response into python.
                                # If unable to serialize then break out of the function
                                try:
                                    sage_disc_responsedict = json.loads(sage_disc_responsestr)
                                except:
                                    error_message += "\nError serializing SAGE response: " + sage_disc_responsestr
                        except Exception as e:
                            error_message += "\nAn exception occurred discontinuing the SAGE product: {0}".format(traceback.format_exc())

                        # If the response was NOT ok then set an error
                        if sage_disc_responsedict['Responses'][0]['OK'] == "0":
                            error_message += "\nsage_disc_responsedict['Responses'][0]['Errors']"
                        else:
                            success_message += "Sage discontinue request was successful"
                        if product_id:
                            message = success_message if success_message else error_message
                            if success_message:
                                product_id.message_post(body=message, message_type='comment', subtype='mail.mt_comment')
                            else:
                                self.env['mail.message'].create({
                                    'email_from': self.env.user.partner_id.email,
                                    'author_id': self.env.user.partner_id.id,
                                    'model': 'product.template',
                                    'type': 'comment',
                                    'subtype_id': self.env.ref('mail.mt_comment').id,
                                    'body': message,
                                    'channel_ids': [(4, self.env.ref('__export__.mail_channel_31_25a840a1').id)],
                                    'res_id': product_id.id,
                                })


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