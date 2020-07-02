# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
import urllib.request
import json
import smtplib


class tmg_product_template_tags(models.Model):
    _name = 'product.template.tags'
    _description = "Product Tags"

    name = fields.Char(string='Name',required=True)
    color = fields.Integer(string='Color Index')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists!"),
    ]


class ProductAttribute(models.Model):
    _inherit = 'product.attribute'

    category = fields.Selection([
        ('decoration', 'Decoration'),
        ('location', 'Location'),
        ('thickness', 'Thickness'),
        ('prodcolor', 'Product Color'),
        ('impcolor', 'Imprint Color'),
        ('config', 'Config')
    ], string='Category')


class ProductExternalCategories(models.Model):
    _name = 'product.external.categories'
    _description = 'External Product Categories'

    name = fields.Char(string='External Category Name', help='The name of category as defined by the external source',
                       required=True)
    external_source = fields.Selection([
        ('asi', 'ASI'),
        ('sage', 'SAGE')
    ], string='External Category Source', help='The external category source', required=True)
    external_id = fields.Char(string='External ID', help='The id of the category as defined by the external source')

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
    def _send_error_email(self, message):

        Mail = self.env['mail.mail']

        values = {
            'model': None,
            'res_id': None,
            'subject': 'SAGE/ASI Category Import Error',
            'body': message,
            'body_html': message,
            'email_from': 'noreply@themagnetgroup.com',
            'email_to': 'jtemple@themagnetgroup.com'
        }
        Mail.create(values).send()

    def set_sage_credentials(self):
        # Get the account and credentials needed for the SAGE request
        acctid = self.env['tmg_external_api.tmg_reference'].search([('category','=','SAGEAuth'),('name','=','AcctId')])
        token = self.env['tmg_external_api.tmg_reference'].search([('category','=','SAGEAuth'),('name','=','Token')])
        sagenum = self.env['tmg_external_api.tmg_reference'].search([('category','=','SAGEAuth'),('name','=','SAGENum')])

        # Set the values in the credentials dictionary
        self.SAGERequest['Request'] = 'CategoryList'
        self.SAGERequest['Auth']['AcctID'] = acctid.value
        self.SAGERequest['Auth']['Token'] = token.value
        self.SAGERequest['Auth']['SAGENum'] = sagenum.value

    def get_asi_auth_token(self):
        # Get the account and credentials needed for the SAGE request
        asi = self.env['tmg_external_api.tmg_reference'].search([('category','=','ASIAuth'),('name','=','Asi')])
        username = self.env['tmg_external_api.tmg_reference'].search([('category','=','ASIAuth'),('name','=','Username')])
        password = self.env['tmg_external_api.tmg_reference'].search([('category','=','ASIAuth'),('name','=','Password')])

        self.ASIAuth['Asi'] = asi.value
        self.ASIAuth['Username'] = username.value
        self.ASIAuth['Password'] = password.value

        asirequest = urllib.request.Request("https://productservice.asicentral.com/api/v4/Login",
                                            data=json.dumps(self.ASIAuth).encode('utf-8'),
                                            headers={'Content-type': 'application/json'},
                                            method='POST')
        try:
            with urllib.request.urlopen(asirequest) as asiresponse:
                # Read the entire response
                asiresponsestr = asiresponse.read().decode('utf-8')
                # Serialize the response into python. If unable to serialize then break out of the function
                try:
                    asiresponsedict = json.loads(asiresponsestr)
                except:
                    self._send_error_email('Error serializaing ASI response: ' + asiresponsestr)
                    return

                # If the response contains a 'Message' then something didn't work
                if "Message" in asiresponsedict:
                    self._send_error_email('ASI error message returned' + asiresponsedict['Message'])
                    return

                # If the response does NOT contain 'AccessToken'
                if "AccessToken"  not in asiresponsedict:
                    self._send_error_email('ASI authorization returned no token')
                    return

                # Get the token and return
                return asiresponsedict['AccessToken']
        except Exception as e:
            self._send_error_email("An exception occurred during retrieval of the ASI access token: " % str(e))

    def load_sage_categories(self):

        self.set_sage_credentials()

        # Capture the current date/time so we can do a reverse check of any category that is no longer in SAGE
        cur_date = datetime.now()

        sagerequest = urllib.request.Request("https://www.promoplace.com/ws/ws.dll/SITK",
                                             data=json.dumps(self.SAGERequest).encode('utf-8'),
                                             method='POST')
        # General catch all
        try:
            with urllib.request.urlopen(sagerequest) as sageresponse:
                # Read the entire response
                sageresponsestr = sageresponse.read().decode('utf-8')
                # Serialize the response into python. If unable to serialize then break out of the function
                try:
                    sageresponsedict = json.loads(sageresponsestr)
                except:
                    self._send_error_email('Error serializing SAGE response: ' + sageresponsestr)
                    return

                # Did by chance SAGE return an error in the response? If so...bail out
                if "ErrMsg" in sageresponsedict:
                    self._send_error_email('SAGE error message returned: ' + sageresponsedict['ErrMsg'])
                    return

                # And one last check to ensure the categories were in the dictionary
                if "Categories" not in sageresponsedict:
                    self._send_error_email('No Categories found in SAGE response string: ' + str(sageresponsedict))
                    return

                # Check each category and either write or update the name
                for category in sageresponsedict['Categories']:
                    ec = self.env['product.external.categories'].search([('external_source', '=', 'sage'),
                                                                         ('external_id', '=', category['ID'])])
                    if len(ec.ids) == 0:
                        ec.create({
                            'name': category['Name'],
                            'external_id': category['ID'],
                            'external_source': 'sage'
                        })
                    else:
                        ec.write({
                            'name': category['Name']
                        })

                # Now look for any categories that we have but are not in SAGE. We'll do this by searching for any
                # category that was not updated on or after the timestamp we captured at the beginning of the routine
                orphaned_categories = self.env['product.external.categories'].search([('external_source','=','sage'),
                                                                                      ('write_date','<',cur_date.strftime("%Y-%m-%d %H:%M:%S"))])
                for oc in orphaned_categories:
                    oc.unlink()
        except Exception as err:
            self._send_error_email("An exception occurred during the SAGE category import: " % str(err))

    def load_asi_categories(self):

        # Capture the current date/time so we can do a reverse check of any category that is no longer in ASI
        cur_date = datetime.now()

        # Get the ASI authorization token. If no token then return
        asitoken = self.get_asi_auth_token()
        if not asitoken:
            return

        asirequest = urllib.request.Request("https://productservice.asicentral.com/api/v4/lookup/categoriesList",
                                            method='GET',
                                            headers={"Authorization": "Bearer %s" % asitoken,
                                                     "Content-type": "application/json"})

        try:
            with urllib.request.urlopen(asirequest) as asiresponse:
                # Read the entire response
                asiresponsestr = asiresponse.read().decode('utf-8')
                # Serialize the response into python. If unable to serialize then break out of the function
                try:
                    asiresponsedict = json.loads(asiresponsestr)
                except:
                    self._send_error_email('Error serializing ASI response: ' + asiresponsestr)
                    return

                # And one last check to ensure the categories were in the dictionary
                if "categories" not in asiresponsedict:
                    self._send_error_email('No Categories found in ASI response string: ' + str(asiresponsedict))
                    return

                # Check each category and either write or update the name
                for category in asiresponsedict['categories']:
                    ec = self.env['product.external.categories'].search([('external_source', '=', 'asi'),
                                                                         ('name', '=', category)])
                    if len(ec.ids) == 0:
                        ec.create({
                            'name': category,
                            'external_source': 'asi'
                        })
                    else:
                        ec.write({
                            'name': category
                        })

                # Now look for any categories that we have but are not in ASI. We'll do this by searching for any
                # category that was not updated on or after the timestamp we captured at the beginning of the routine
                orphaned_categories = self.env['product.external.categories'].search([('external_source','=','asi'),
                                                                                      ('write_date','<',cur_date.strftime("%Y-%m-%d %H:%M:%S"))])
                for oc in orphaned_categories:
                    oc.unlink()

        except Exception as err:
            self._send_error_email("An error occurred during the ASI category import: " % str(err))


class ProductPublicCategory(models.Model):
    _inherit = 'product.public.category'

    asi_category_id = fields.Many2one(comodel_name='product.external.categories', string='ASI Category',
                                      ondelete='set null')
    sage_category_id = fields.Many2one(comodel_name='product.external.categories', string='SAGE Category',
                                       ondelete='set null')


class ProductDecorationMethod(models.Model):
    _name = 'product.template.decorationmethod'
    _description = 'Product Decoration Method'

    product_tmpl_id = fields.Many2one(comodel_name='product.template', string='Product Template')
    decoration_method_id = fields.Many2one(comodel_name='product.template.attribute.value', string='Decoration Method',
                                           delete='restrict', required=True)
    prod_time_lo = fields.Integer(string='Production Time Low',
                                  help='Lowest decoration time (in days) for this product and decoration method',
                                  required=True)
    prod_time_hi = fields.Integer(string='Production Time High',
                                  help='Highest decoration time (in days) for this product and decoration method',
                                  required=True)
    quick_ship = fields.Boolean(string='Quick Ship Available',
                                help='Is Quick Ship available for this product and decoration method',
                                required=True)
    quick_ship_prod_days = fields.Integer(string='Quick Ship Production Days',
                                          help='If quick ship is available, the number of production days required')
    quick_ship_max = fields.Integer(string='Quick Ship Maximum Quantity',
                                    help='If quick ship is available the maximum quantity that can be shipped')
    number_sides = fields.Integer(string='Number Sides Included', default=1,
                                  help='Number of decoration locations included for this product and decoration method',
                                  required=True)
    pms = fields.Boolean(string='PMS Available', help='Is Pantone color matching available for this product and decoration method',
                         required=True)
    full_color = fields.Boolean(string='Full Color Available', help='Is Full Colro decoration avaiable for this product and decoration method',
                                required=True)
    max_colors = fields.Boolean(string='Maximum Decoration colors',
                                help='Maximum number of colors that can be used for this product and decoration method',
                                required=True)


class ProductDecorationArea(models.Model):
    _name = 'product.template.decorationarea'
    _description = 'Product Decoration Area'

    product_tmpl_id = fields.Many2one(comodel_name='product.template', string='Product Template', ondelete='restrict')
    decoration_area_id = fields.Many2one(comodel_name='product.template.attribute.value')
    decoration_method_id = fields.Many2one(comodel_name='product.template.decorationmethod', string='Decoration Method')
    height = fields.Float(string='Decoration Height', help='The height of the decoration area in inches.')
    width = fields.Float(string='Decoration Width', help='The width of the decoration area in inches.')
    shape = fields.Selection([
        ('Circle'),
        ('Rectangle'),
        ('Other')
    ], string='Decoration Shape')
    diameter = fields.Float(string='Decoration Diameter', help='The diameter of the decoration area in inches.')
    dimensions = fields.Char(string='Dimensions', compute='_compute_dimensions', store=False)

    @api.depends('width', 'height')
    def _compute_dimensions(self):
        for decoarea in self:
            dimensions = None
            if decoarea.depth and decoarea.width:
                dimensions = "{width:.2f}\" x {height:.2f}\"".format(width=decoarea.width, height=decoarea.height)
            decoarea.dimensions = dimensions


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    decoration_method_ids = fields.One2many(comodel_name='product.template.decorationmethod', inverse_name='product_tmpl_id')
    decoration_area_ids = fields.One2many(comodel_name='product.template.decorationarea', inverse_name='decoration_area_id')

