# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
# from odoo.addons import decimal_precision as dp
from datetime import datetime
import urllib.request
import json
import base64
import traceback
# import xml.etree.ElementTree as ET
from lxml import etree as ET


class tmg_product_template_tags(models.Model):
    _name = 'product.template.tags'
    _description = "Product Tags"

    name = fields.Char(string='Name', required=True)
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
        acctid = self.env['tmg_external_api.tmg_reference'].search(
            [('category', '=', 'SAGEAuth'), ('name', '=', 'AcctId')])
        token = self.env['tmg_external_api.tmg_reference'].search(
            [('category', '=', 'SAGEAuth'), ('name', '=', 'Token')])
        sagenum = self.env['tmg_external_api.tmg_reference'].search(
            [('category', '=', 'SAGEAuth'), ('name', '=', 'SAGENum')])

        # Set the values in the credentials dictionary
        self.SAGERequest['Request'] = 'CategoryList'
        self.SAGERequest['Auth']['AcctID'] = acctid.value
        self.SAGERequest['Auth']['Token'] = token.value
        self.SAGERequest['Auth']['SAGENum'] = sagenum.value

    def get_asi_auth_token(self):
        # Get the account and credentials needed for the SAGE request
        asi = self.env['tmg_external_api.tmg_reference'].search([('category', '=', 'ASIAuth'), ('name', '=', 'Asi')])
        username = self.env['tmg_external_api.tmg_reference'].search(
            [('category', '=', 'ASIAuth'), ('name', '=', 'Username')])
        password = self.env['tmg_external_api.tmg_reference'].search(
            [('category', '=', 'ASIAuth'), ('name', '=', 'Password')])

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
                if "AccessToken" not in asiresponsedict:
                    self._send_error_email('ASI authorization returned no token')
                    return

                # Get the token and return
                return asiresponsedict['AccessToken']
        except Exception as e:
            self._send_error_email("An exception occurred during retrieval of the ASI access token: {0}".format(traceback.format_exc()))

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
                orphaned_categories = self.env['product.external.categories'].search([('external_source', '=', 'sage'),
                                                                                      ('write_date', '<',
                                                                                       cur_date.strftime(
                                                                                           "%Y-%m-%d"))])
                for oc in orphaned_categories:
                    oc.unlink()
        except Exception as err:
            self._send_error_email("An exception occurred during the SAGE category import: {0}".format(traceback.format_exc()))

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
                orphaned_categories = self.env['product.external.categories'].search([('external_source', '=', 'asi'),
                                                                                      ('write_date', '<',
                                                                                       cur_date.strftime(
                                                                                           "%Y-%m-%d"))])
                for oc in orphaned_categories:
                    oc.unlink()

        except Exception as err:
            self._send_error_email("An error occurred during the ASI category import: {0}".format(traceback.format_exc()))


class ProductPublicCategory(models.Model):
    _inherit = 'product.public.category'

    asi_category_id = fields.Many2one(comodel_name='product.external.categories', string='ASI Category',
                                      ondelete='set null')
    sage_category_id = fields.Many2one(comodel_name='product.external.categories', string='SAGE Category',
                                       ondelete='set null')


class ProductDecorationMethod(models.Model):
    _name = 'product.template.decorationmethod'
    _description = 'Product Decoration Method'

    name = fields.Char(string='Name', compute='_set_name')
    product_tmpl_id = fields.Many2one(comodel_name='product.template', string='Product Template', required=True)
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
    pms = fields.Boolean(string='PMS Available',
                         help='Is Pantone color matching available for this product and decoration method',
                         required=True)
    full_color = fields.Boolean(string='Full Color Available',
                                help='Is Full Colro decoration avaiable for this product and decoration method',
                                required=True)
    max_colors = fields.Integer(string='Maximum Decoration colors',
                                help='Maximum number of colors that can be used for this product and decoration method',
                                required=True)

    @api.depends('decoration_method_id')
    def _set_name(self):
        for method in self:
            method.name = method.decoration_method_id.name


class ProductDecorationArea(models.Model):
    _name = 'product.template.decorationarea'
    _description = 'Product Decoration Area'

    name = fields.Char(string='Name', compute='_set_name')
    product_tmpl_id = fields.Many2one(comodel_name='product.template', string='Product Template', ondelete='restrict',
                                      required=True)
    decoration_area_id = fields.Many2one(comodel_name='product.template.attribute.value', string='Decoration Area',
                                         required=True)
    decoration_method_id = fields.Many2one(comodel_name='product.template.decorationmethod', string='Decoration Method',
                                           required=True)
    height = fields.Float(string='Decoration Height', help='The height of the decoration area in inches.')
    width = fields.Float(string='Decoration Width', help='The width of the decoration area in inches.')
    shape = fields.Selection([
        ('circle', 'Circle'),
        ('rectangle', 'Rectangle'),
        ('other', 'Other')
    ], string='Decoration Shape', required=True)
    diameter = fields.Float(string='Decoration Diameter', help='The diameter of the decoration area in inches.')
    dimensions = fields.Char(string='Dimensions', compute='_compute_dimensions', store=False)

    @api.depends('width', 'height')
    def _compute_dimensions(self):
        for decoarea in self:
            dimensions = None
            if decoarea.width and decoarea.height:
                dimensions = "{width:.2f}\" x {height:.2f}\"".format(width=decoarea.width, height=decoarea.height)
            decoarea.dimensions = dimensions

    @api.depends('decoration_area_id', 'decoration_method_id')
    def _set_name(self):
        for area in self:
            area.name = area.decoration_area_id.name

    @api.constrains('shape')
    def _check_shape(self):
        if self.shape == 'circle' and self.diameter == 0:
            raise ValidationError("If the shape is a circle then diameter cannot be 0!")


class ProductAdditonalCharges(models.Model):
    _name = 'product.addl.charges'
    _description = 'Product Addtional Charges'

    product_tmpl_id = fields.Many2one(comodel_name='product.template', string='Product Template', ondelete='restrict',
                                      required=True)
    addl_charge_product_id = fields.Many2one(comodel_name='product.template', string='Additional Charge Product',
                                             ondelete='restrict', required=True)
    decoration_method_ids = fields.Many2many(comodel_name='product.template.attribute.value',
                                             string='Decoration Methods')
    charge_type = fields.Selection([
        ('order', 'Order'),
        ('run', 'Run'),
        ('setup', 'Setup')
    ], string='Charge Type', required=True)
    charge_yuom = fields.Selection([
        ('colors', 'Colors'),
        ('inches', 'Inches'),
        ('other', 'Other'),
        ('stitches', 'Stitches'),
        ('squareinches', 'Square Inches')
    ], string='Charge Secondary UOM', required=True)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    decoration_method_ids = fields.One2many(comodel_name='product.template.decorationmethod',
                                            inverse_name='product_tmpl_id')
    decoration_area_ids = fields.One2many(comodel_name='product.template.decorationarea',
                                          inverse_name='product_tmpl_id')
    addl_charge_product_ids = fields.One2many(comodel_name='product.addl.charges', inverse_name='product_tmpl_id')
    data_errors = fields.Html(string='Required Data Errors')

    @api.constrains('decoration_method_ids')
    def _check_deco_methods(self):

        if any(len(template.decoration_method_ids) != len(template.decoration_method_ids.mapped('decoration_method_id'))
               for template in self):
            raise ValidationError('You cannot have the same decoration method on multiple lines!')
        return True

    def _build_all_xml(self):
        # Get a list of all active products that can be sold
        products = self.env['product.template'].search(
            [('active', '=', True), ('sale_ok', '=', True), ('website_published', '=', True), ('type', '=', 'product')])
        for product in products:
            product._build_std_xml()

    # In this routine we will check all required data elements to build the product XML and if any are missing
    # we'll update the data error messages field on this product and return false
    def _check_xml_data(self):
        messages = []

        if not self.product_style_number:
            messages.append("<li>Product Style Number missing</li>")
        if not self.name:
            messages.append("<li>Product Name missing</li>")
        if not self.categ_id:
            messages.append("<li>Product Category missing</li>")
        if not self.website_description:
            messages.append("<li>Product Website Description missing</li>")
        if not self.width:
            messages.append("<li>Product Width missing</li>")
        if not self.height:
            messages.append("<li>Product Height missing</li>")
        if not self.depth:
            messages.append("<li>Product Depth missing</li>")
        if not self.product_variant_count or self.product_variant_count == 0:
            messages.append("<li>Product does not have variants configured</li>")
        if not self.primary_material:
            messages.append("<li>Product Primary Material missing</li>")
        if not self.market_introduction_date:
            messages.append("<li>Product Market Introduction Date missing</li>")
        if not self.website_meta_keywords:
            messages.append("<li>Product Keywords missing</li>")
        if not self.public_categ_ids:
            messages.append("<li>Product Website Categories missing</li>")
        else:
            for cat in self.public_categ_ids:
                if cat.parent_id.name == "Category":
                    if not cat.sage_category_id:
                        messages.append("<li>Product Category '{0}' missing equivalent SAGE category</li>".format(cat.name))
                    if not cat.asi_category_id:
                        messages.append("<li>Product Category '{0}' missing equivalent ASI category</li>".format(cat.name))
        if not self.warehouses:
            messages.append("<li>Product Warehouse(s) missing</li>")
        else:
            for warehouse in self.warehouses:
                if not warehouse.partner_id:
                    messages.append("<li>Product Warehouse '{0}' missing address entry</li>".format(warehouse.name))
                else:
                    if not warehouse.partner_id.zip:
                        messages.append("<li>Product Warehouse '{0}' Address missing zip code</li>".format(warehouse.name))
                    if not warehouse.partner_id.city:
                        messages.append("<li>Product Warehouse '{0}' Address missing city</li>".format(warehouse.name))
                    if not warehouse.partner_id.state_id:
                        messages.append("<li>Product Warehouse '{0}' Address missing state</li>".format(warehouse.name))
                    if not warehouse.partner_id.country_id:
                        messages.append("<li>Product Warehouse '{0}' Address missing country</li>".format(warehouse.name))
        if self.product_variant_ids:
            for variant in self.product_variant_ids:
                if not variant.name:
                    messages.append("<li>Product Variant missing name</li>")
                if not variant.weight:
                    messages.append("<li>Product Variant '{0}' missing weight</li>".format(variant.weight))
                if not variant.default_code:
                    messages.append("<li>Product Variant '{0}' missing internal reference</li>".format(variant.display_name))
                if not variant.default_code:
                    messages.append("<li>Product Variant '{0}' missing default code</li>".format(variant.display_name))
                if not variant.packaging_ids:
                    messages.append("<li>Product Variant '{0}' missing packaging ids</li>".format(variant.display_name))
                else:
                    if not variant.packaging_ids[0].name:
                        messages.append("<li>Product Variant '{0}' packaging missing name</li>".format(variant.display_name))
                    if not variant.packaging_ids[0].qty:
                        messages.append("<li>Product Variant '{0}' packaging missing quantity</li>".format(variant.display_name))
                    if not variant.packaging_ids[0].max_weight:
                        messages.append("<li>Product Variant '{0}' packaging missing maximum weight</li>".format(variant.display_name))
                    if not variant.packaging_ids[0].length:
                        messages.append("<li>Product Variant '{0}' packaging missing length</li>".format(variant.display_name))
                    if not variant.packaging_ids[0].width:
                        messages.append("<li>Product Variant '{0}' packaging missing width</li>".format(variant.display_name))
                    if not variant.packaging_ids[0].height:
                        messages.append("<li>Product Variant '{0}' packaging missing height</li>".format(variant.display_name))
        else:
            messages.append("<li>Product has no variants</li>")
        if not self.decoration_method_ids:
            messages.append("<li>Product missing decoration methods</li>")
        else:
            for method in self.decoration_method_ids:
                if not method.name:
                    messages.append("<li>Decoration method for product missing name</li>")
                if not method.prod_time_lo:
                    messages.append("<li>Decoration method '{0}' missing production time low</li>".format(method.name))
                if not method.prod_time_hi:
                    messages.append("<li>Decoration method '{0}' missing production time high</li>".format(method.name))
                if method.quick_ship:
                    if not method.quick_ship_max:
                        messages.append("<li>Decoration method '{0}' flagged for quick ship but missing quick ship max quantity</li>".format(method.name))
                    if not method.quick_ship_prod_days:
                        messages.append("<li>Decoration method '{0}' flagged for quick ship but missing quick ship production days</li>".format(method.name))
                # if not method.number_sides:
                #     messages.append("<li>Decoration method '{0}' missing number of sides</li>".format(method.name))
                # Set the variants that don't create attributes in the context
                self = self.with_context(no_create_variant_attributes=[method.decoration_method_id.id])
                # Build the price grid for standard catalog/net
                price_grid_dict = self._build_price_grid()
                if len(price_grid_dict) == 0:
                    messages.append("<li>Pricing not returned for product</li>")

        if not self.decoration_area_ids:
            messages.append("<li>Product missing decoration locations</li>")
        else:
            for area in self.decoration_area_ids:
                if not area.height:
                    messages.append("<li>Decoration area '{0}' missing height</li>".format(area.name))
                if not area.width:
                    messages.append("<li>Decoration area '{0}' missing width</li>".format(area.name))
                if area.shape == "circle" and (not area.diameter or area.diameter == 0):
                    messages.append("<li>Decoration area '{0}' shape is circle but no diameter specified</li>".format(area.name))
                if not area.shape:
                    messages.append("<li>Decoration area '{0}' missing shape</li>".format(area.name))
        if self.addl_charge_product_ids:
            for ac in self.addl_charge_product_ids:
                if not ac.charge_type:
                    messages.append("<li>Additional Charge Item '{0}' missing charge type</li>".format(ac.product_tmpl_id.name))
                if not ac.charge_yuom:
                    messages.append("<li>Additional Charge Item '{0}' missing other unit of measure</li>".format(ac.product_tmpl_id.name))
                # Build the price grid for standard catalog/net
                ac_price_grid_dict = ac.product_tmpl_id._build_price_grid()
                if len(ac_price_grid_dict) == 0:
                    messages.append("<li>No pricing found for additional charge item '{0}'</li>".format(ac.product_tmpl_id.name))

        # Now if we wrote ANY messages to the messages list update the data error message field
        if len(messages):
            error_text = '<ul>' + ''.join(messages) + '</ul>'
            self.write({
                'data_errors': error_text
            })
            return False
        else:
            self.write({
                'data_errors': None
            })
            return True

    def _build_std_xml(self):

        # First check if we have any data issues for building this XML. If so, return and don't build the data
        if not self._check_xml_data():
            return
        try:
            # Get Odoo's decimal accuracy for pricing
            price_digits = self.env['decimal.precision'].precision_get('Product Price')
            # Set the folder for uploading product documents to S3
            prod_folder = self.product_style_number + '/'
            # First we will build the standard XML for the product.
            product = ET.Element('product')
            ET.SubElement(product, "product_style_number").text = self.product_style_number
            ET.SubElement(product, "product_id").text = str(self.id)
            ET.SubElement(product, "product_name").text = self.name
            # The name of the product's category is the product category. The name of the top category in the path
            # is the brand
            ET.SubElement(product, "brand_name").text = self.categ_id.get_parent_name()
            ET.SubElement(product, "category_name").text = self.categ_id.name
            ET.SubElement(product, "website_description").text = self.website_description
            ET.SubElement(product, "width").text = str(self.width)
            ET.SubElement(product, "height").text = str(self.height)
            ET.SubElement(product, "dimensions").text = self.dimensions
            ET.SubElement(product, "depth").text = str(self.depth)
            # The weight will come from the first variant
            if self.product_variant_ids:
                ET.SubElement(product, "weight").text = str(self.product_variant_ids[0].weight)
            # Get the res.config.settings model. If not found assume pounds
            config = self.env['ir.config_parameter']
            product_weight_in_lbs = config.get_param('product.weight_in_lbs', False)
            if product_weight_in_lbs == "1":
                ET.SubElement(product, "weight_uom").text = "LB"
            else:
                ET.SubElement(product, "weight_uom").text = "KG"
            ET.SubElement(product, "product_variant_count").text = str(self.product_variant_count)
            ET.SubElement(product, "primary_material").text = self.primary_material
            ET.SubElement(product, "pricing_year").text = str(datetime.now().year)
            if self.market_introduction_date:
                ET.SubElement(product, "market_introduction_date").text = datetime.strftime(self.market_introduction_date, "%Y-%m-%d")
            else:
                ET.SubElement(product, "market_introduction_date").text = ""
            if self.data_last_change_date:
                ET.SubElement(product, "data_last_change_date").text = datetime.strftime(self.data_last_change_date, "%Y-%m-%d")
            else:
                ET.SubElement(product, "data_last_change_date").text = ""
            # Split the keywords for the product
            if self.website_meta_keywords:
                keyword_elem = ET.SubElement(product, "website_meta_keywords")
                keywords = self.website_meta_keywords.split(", ")
                for keyword in keywords:
                    ET.SubElement(keyword_elem, "keyword").text = keyword
            product_tags_elem = ET.SubElement(product, "product_tags")
            for tag in self.product_tags_ids:
                ET.SubElement(product_tags_elem, "product_tag").text = tag.name
            # Website tags will be any e-commerce category with a parent of "Tags"
            website_tags_elem = ET.SubElement(product, "website_tags")
            for category in self.public_categ_ids:
                if category.parent_id.name == 'Tags':
                    ET.SubElement(website_tags_elem, "website_tag").text = category.name
            # Website categories will be any e-commerce category with a parent of "Category".  This will also establish
            # the link between our website category and ASI/SAGE category.
            website_cats_elem = ET.SubElement(product, "product_categories")
            for category in self.public_categ_ids:
                if category.parent_id.name == "Category":
                    website_cat_elem = ET.SubElement(website_cats_elem, "product_category")
                    ET.SubElement(website_cat_elem, "name").text = category.name
                    ET.SubElement(website_cat_elem, "sage_category").text = category.sage_category_id.name
                    ET.SubElement(website_cat_elem, "sage_category_id").text = category.sage_category_id.external_id
                    ET.SubElement(website_cat_elem, "asi_category").text = category.asi_category_id.name
            alt_products_elem = ET.SubElement(product, "alternative_products")
            for alt_product in self.alternative_product_ids:
                ET.SubElement(alt_products_elem, "alternative_product").text = alt_product.product_style_number
            warehouses_elem = ET.SubElement(product, "warehouses")
            for warehouse in self.warehouses:
                warehouse_elem = ET.SubElement(warehouses_elem, "warehouse")
                ET.SubElement(warehouse_elem, "name").text = warehouse.name
                ET.SubElement(warehouse_elem, "zip").text = warehouse.partner_id.zip
                ET.SubElement(warehouse_elem, "city").text = warehouse.partner_id.city
                ET.SubElement(warehouse_elem, "state").text = warehouse.partner_id.state_id.code
                ET.SubElement(warehouse_elem, "country").text = warehouse.partner_id.country_id.name
                ET.SubElement(warehouse_elem, "code").text = warehouse.code
            # Start images nodes
            images_elem = ET.SubElement(product, "images")
            # In order to upload products images we need to ensure we've established a public bucket
            s3 = self.env['pr1_s3.s3_connection'].search([('name', '=', 'tmg-public')])
            if s3:
                # Upload the large image
                if self.image:
                    image_url = s3._upload_to_public_bucket(self.image, self.product_style_number + '.jpg', 'image/jpeg', prod_folder)
                    ET.SubElement(images_elem, "image").text = image_url
                # Upload the medium image
                if self.image_medium:
                    image_url = s3._upload_to_public_bucket(self.image_medium, self.product_style_number + '_medium.jpg', 'image/jpeg', prod_folder)
                    ET.SubElement(images_elem, "image_medium").text = image_url
                # Upload the small image
                if self.image_small:
                    image_url = s3._upload_to_public_bucket(self.image_small, self.product_style_number + '_small.jpg', 'image/jpeg', prod_folder)
                    ET.SubElement(images_elem, "image_small").text = image_url

                # If there are any additional product images upload those
                if self.product_image_ids:
                    extra_images_elem = ET.SubElement(images_elem, "additional_images")
                    for image in self.product_image_ids:
                        image_url = s3._upload_to_public_bucket(image.image, image.name + ".jpg", "image/jpeg", prod_folder)
                        ET.SubElement(extra_images_elem, "additional_image").text = image_url

            # If the product has variants then add those.
            pvs_elem = ET.SubElement(product, "product_variants")
            if self.product_variant_ids:
                # Loop through the product.products and add variant specific information
                for variant in self.product_variant_ids:
                    pv_elem = ET.SubElement(pvs_elem, "product_variant")
                    ET.SubElement(pv_elem, "product_variant_id").text = str(variant.id)
                    ET.SubElement(pv_elem, "product_variant_number").text = variant.default_code
                    ET.SubElement(pv_elem, "product_variant_name").text = variant.name
                    # Here we'll write the first attribute value that has a category of 'color' or 'thickness'
                    for attribute_value in variant.attribute_value_ids:
                        if attribute_value.attribute_id.category in ('prodcolor', 'thickness'):
                            ET.SubElement(pv_elem, "product_variant_swatch").text = attribute_value.html_color
                            ET.SubElement(pv_elem, "product_variant_color").text = attribute_value.name
                            break
                    # Write the packaging information for this product variant. We will only write out the first packaging
                    # row
                    if variant.packaging_ids:
                        pkg_elem = ET.SubElement(pv_elem, "packaging")
                        ET.SubElement(pkg_elem, "packaging_id").text = str(variant.packaging_ids[0].id)
                        ET.SubElement(pkg_elem, "name").text = variant.packaging_ids[0].name
                        ET.SubElement(pkg_elem, "qty").text = str(variant.packaging_ids[0].qty)
                        ET.SubElement(pkg_elem, "max_weight").text = str(variant.packaging_ids[0].max_weight)
                        ET.SubElement(pkg_elem, "length").text = str(variant.packaging_ids[0].length)
                        ET.SubElement(pkg_elem, "width").text = str(variant.packaging_ids[0].width)
                        ET.SubElement(pkg_elem, "height").text = str(variant.packaging_ids[0].height)
                    # Write the attributes that are specific to this variant (color, thickness, etc)
                    # In order for attributes to appear in the standard XML they must have an attribute category
                    attrs_elem = ET.SubElement(pv_elem, "attributes")
                    for attribute_value in variant.attribute_value_ids:
                        if attribute_value.attribute_id.category:
                            attr_elem = ET.SubElement(attrs_elem, "attribute")
                            ET.SubElement(attr_elem, "attribute_category").text = attribute_value.attribute_id.category
                            ET.SubElement(attr_elem, "attribute_id").text = str(attribute_value.id)
                            ET.SubElement(attr_elem, "attribute_name").text = attribute_value.attribute_id.name
                            ET.SubElement(attr_elem, "attribute_value").text = attribute_value.name
                            ET.SubElement(attr_elem, "attribute_sequence").text = str(attribute_value.sequence)
                    # Upload the variant's images to public storage
                    pv_images_elem = ET.SubElement(pv_elem, "images")
                    if variant.image:
                        image_url = s3._upload_to_public_bucket(variant.image, variant.default_code + '.jpg', 'image/jpeg', prod_folder)
                        ET.SubElement(pv_images_elem, "image").text = image_url
                    if variant.image_medium:
                        image_url = s3._upload_to_public_bucket(variant.image_medium, variant.default_code + '_medium.jpg', 'image/jpeg', prod_folder)
                        ET.SubElement(pv_images_elem, "image_medium").text = image_url
                    if variant.image_small:
                        image_url = s3._upload_to_public_bucket(variant.image_small, variant.default_code + '_small.jpg', 'image/jpeg', prod_folder)
                        ET.SubElement(pv_images_elem, "image_small").text = image_url
            # Write the decoration location
            if self.decoration_area_ids:
                locations_elem = ET.SubElement(product, "decoration_locations")
                for location in self.decoration_area_ids:
                    location_elem = ET.SubElement(locations_elem, "decoration_location")
                    ET.SubElement(location_elem, "id").text = str(location.decoration_area_id.attribute_id.id)
                    ET.SubElement(location_elem, "name").text = location.name
                    methods_elem = ET.SubElement(location_elem, "decoration_methods")
                    method_elem = ET.SubElement(methods_elem, "decoration_method")
                    ET.SubElement(method_elem, "id").text = str(location.decoration_method_id.decoration_method_id.attribute_id.id)
                    ET.SubElement(method_elem, "name").text = location.decoration_method_id.name
                    ET.SubElement(method_elem, "sequence").text = str(location.decoration_method_id.decoration_method_id.sequence)
                    ET.SubElement(method_elem, "height").text = str(location.height)
                    ET.SubElement(method_elem, "width").text = str(location.width)
                    if location.shape == "circle" and location.diameter and \
                            location.diameter != 0:
                        ET.SubElement(method_elem, "diameter").text = str(location.diameter)
                    ET.SubElement(method_elem, "dimensions").text = location.dimensions
                    ET.SubElement(method_elem, "shape").text = location.shape
                    ET.SubElement(method_elem, "prod_time_lo").text = str(location.decoration_method_id.prod_time_lo)
                    ET.SubElement(method_elem, "prod_time_hi").text = str(location.decoration_method_id.prod_time_hi)
                    ET.SubElement(method_elem, "quick_ship").text = str(location.decoration_method_id.quick_ship)
                    ET.SubElement(method_elem, "quick_ship_max").text = str(location.decoration_method_id.quick_ship_max)
                    ET.SubElement(method_elem, "quick_ship_prod_days").text = str(location.decoration_method_id.quick_ship_prod_days)
                    ET.SubElement(method_elem, "number_sides").text = str(location.decoration_method_id.number_sides)
                    ET.SubElement(method_elem, "pms").text = str(location.decoration_method_id.pms)
                    ET.SubElement(method_elem, "full_color").text = str(location.decoration_method_id.full_color)
                    ET.SubElement(method_elem, "max_colors").text = str(location.decoration_method_id.max_colors)

                    # Now write the prices.  First get the pricing grid
                    prices_elem = ET.SubElement(method_elem, "prices")
                    price_elem = ET.SubElement(prices_elem, "price")
                    # Set the variants that don't create attributes in the context
                    self = self.with_context(no_create_variant_attributes=[location.decoration_method_id.decoration_method_id.id])
                    # Build the price grid for standard catalog/net
                    price_grid_dict = self._build_price_grid()
                    self = self.with_context(no_create_variant_attributes=None)
                    # Write the catalog price structure
                    ET.SubElement(price_elem, "name").text = price_grid_dict['catalog_pricelist']
                    ET.SubElement(price_elem, "currency_id").text = price_grid_dict['catalog_currency']
                    ET.SubElement(price_elem, "ala_catalog").text = str(price_grid_dict['catalog_prices'][-1])
                    ET.SubElement(price_elem, "ala_net").text = str(price_grid_dict['net_prices'][-1])
                    ET.SubElement(price_elem, "ala_discount_code").text = price_grid_dict['discount_codes'][-1]
                    ET.SubElement(price_elem, "uom").text = self.uom_name
                    quantities_elem = ET.SubElement(price_elem, "quantities")
                    for idx, qty in enumerate(price_grid_dict['quantities'], start=0):
                        quantity_elem = ET.SubElement(quantities_elem, "quantity")
                        ET.SubElement(quantity_elem, "min_quantity").text = str(qty)
                        ET.SubElement(quantity_elem, "catalog_price").text = "{price:.{dp}f}".format(price=price_grid_dict['catalog_prices'][idx], dp=price_digits)
                        ET.SubElement(quantity_elem, "discount_code").text = str(price_grid_dict['discount_codes'][idx])
                        ET.SubElement(quantity_elem, "net_price").text = "{price:.{dp}f}".format(price=price_grid_dict['net_prices'][idx], dp=price_digits)
                        ET.SubElement(quantity_elem, "date_start").text = str(price_grid_dict['effective_dates'][idx])
                        ET.SubElement(quantity_elem, "date_end").text = str(price_grid_dict['expiration_dates'][idx])

                    # Now write the additional charges that apply to this product/decoration method combination
                    if self.addl_charge_product_ids:
                        addl_charges_elem = ET.SubElement(method_elem, "additional_charges")
                        for addl_charge_id in self.addl_charge_product_ids:
                            if not addl_charge_id.decoration_method_ids or \
                                    location.decoration_method_id.decoration_method_id.id in \
                                    addl_charge_id.decoration_method_ids.ids:
                                addl_charge_elem = ET.SubElement(addl_charges_elem, "additional_charge")
                                ET.SubElement(addl_charge_elem, "id").text = str(addl_charge_id.id)
                                ET.SubElement(addl_charge_elem, "uom").text = addl_charge_id.addl_charge_product_id.uom_name
                                ET.SubElement(addl_charge_elem, "item_number").text = addl_charge_id.addl_charge_product_id.default_code
                                ET.SubElement(addl_charge_elem, "name").text = addl_charge_id.addl_charge_product_id.name
                                ET.SubElement(addl_charge_elem, "charge_type").text = addl_charge_id.charge_type
                                ET.SubElement(addl_charge_elem, "charge_yuom").text = addl_charge_id.charge_yuom
                                # Build the price grid for standard catalog/net
                                ac_price_grid_dict = addl_charge_id.addl_charge_product_id._build_price_grid()
                                if ac_price_grid_dict:
                                    ET.SubElement(addl_charge_elem, "min_quantity").text = str(ac_price_grid_dict['quantities'][0])
                                    ET.SubElement(addl_charge_elem, "catalog_price").text = "{price:.{dp}f}".format(price=ac_price_grid_dict['catalog_prices'][0], dp=price_digits)
                                    ET.SubElement(addl_charge_elem, "discount_code").text = str(ac_price_grid_dict['discount_codes'][0])
                                    ET.SubElement(addl_charge_elem, "net_price").text = "{price:.{dp}f}".format(price=ac_price_grid_dict['net_prices'][0], dp=price_digits)
                                    ET.SubElement(addl_charge_elem, "date_start").text = str(ac_price_grid_dict['effective_dates'][0])
                                    ET.SubElement(addl_charge_elem, "date_end").text = str(ac_price_grid_dict['expiration_dates'][0])

            # If "Blank" is included in the decoration method table then we need to write out blank pricing for this item
            for method in self.decoration_method_ids:
                if method.name == "Blank":
                    blank_elem = ET.SubElement(product, "blank_pricing")
                    ET.SubElement(blank_elem, "id").text = str(method.decoration_method_id.attribute_id.id)
                    ET.SubElement(blank_elem, "name").text = method.name
                    ET.SubElement(blank_elem, "sequence").text = str(method.decoration_method_id.sequence)
                    ET.SubElement(blank_elem, "prod_time_lo").text = str(method.prod_time_lo)
                    ET.SubElement(blank_elem, "prod_time_hi").text = str(method.prod_time_hi)
                    ET.SubElement(blank_elem, "quick_ship").text = str(method.quick_ship)
                    ET.SubElement(blank_elem, "quick_ship_max").text = str(method.quick_ship_max)
                    ET.SubElement(blank_elem, "quick_ship_prod_days").text = str(method.quick_ship_prod_days)
                    ET.SubElement(blank_elem, "number_sides").text = str(method.number_sides)
                    ET.SubElement(blank_elem, "pms").text = str(method.pms)
                    ET.SubElement(blank_elem, "full_color").text = str(method.full_color)
                    ET.SubElement(blank_elem, "max_colors").text = str(method.max_colors)
                    # Build the price grid for blank pricing
                    price_grid_dict = self._build_price_grid(net_pricelist='Blank')
                    if price_grid_dict:
                        quantities_elem = ET.SubElement(blank_elem, "quantities")
                        for idx, qty in enumerate(price_grid_dict['quantities'], start=0):
                            quantity_elem = ET.SubElement(quantities_elem, "quantity")
                            ET.SubElement(quantity_elem, "min_quantity").text = str(qty)
                            ET.SubElement(quantity_elem, "catalog_price").text = "{price:.{dp}f}".format(price=price_grid_dict['catalog_prices'][idx], dp=price_digits)
                            ET.SubElement(quantity_elem, "discount_code").text = str(
                                price_grid_dict['discount_codes'][idx])
                            ET.SubElement(quantity_elem, "net_price").text = "{price:.{dp}f}".format(price=price_grid_dict['net_prices'][idx], dp=price_digits)
                            ET.SubElement(quantity_elem, "date_start").text = str(
                                price_grid_dict['effective_dates'][idx])
                            ET.SubElement(quantity_elem, "date_end").text = str(
                                price_grid_dict['expiration_dates'][idx])

            # Now write out all the attributes that do not create variants
            if self.attribute_line_ids:
                nc_attributes = self.attribute_line_ids.filtered(lambda r: r.attribute_id.create_variant == 'no_variant')
                if nc_attributes:
                    attributes_elem = ET.SubElement(product, "attributes")
                    for nc_attribute in nc_attributes:
                        attribute_elem = ET.SubElement(attributes_elem, "attribute")
                        ET.SubElement(attribute_elem, "id").text = str(nc_attribute.attribute_id.id)
                        ET.SubElement(attribute_elem, "name").text = nc_attribute.attribute_id.name
                        ET.SubElement(attribute_elem, "category").text = nc_attribute.attribute_id.category
                        attr_values_elem = ET.SubElement(attribute_elem, "values")
                        for attr in nc_attribute.product_template_value_ids:
                            ET.SubElement(attr_values_elem, "id").text = str(attr.product_attribute_value_id.id)
                            ET.SubElement(attr_values_elem, "value").text = attr.name

            # Upload any attachment that has a category
            files_elem = ET.SubElement(product, "files")
            for attach in self.attachment_ids:
                if attach.attachment_category:
                        attach_url = s3._upload_to_public_bucket(attach.datas, attach.name, attach.mimetype, prod_folder)
                        file_elem = ET.SubElement(files_elem, "file", category=attach.attachment_category[0].name).text = attach_url

            # Now we dump the entire XML into a string
            product_xml = base64.b64encode(ET.tostring(product, encoding='utf-8', xml_declaration=True, pretty_print=True))

            # Get attachments for this product that are not attached to a message
            attachment_ids = self.env['ir.attachment'].search([('res_id', '=', self.id),
                                                               ('name', '=', 'product_data.xml'),
                                                               ('res_model', '=', 'product.template')]).ids
            message_attachment_ids = self.mapped('message_ids.attachment_ids').ids  # from mail_thread
            attachment_ids = list(set(attachment_ids) - set(message_attachment_ids))
            # Now delete any file with that name since we will regenerate
            old_product_xml = ''
            write_new_file = False
            if len(attachment_ids) > 0:
                for attach_id in attachment_ids:
                    attach = self.env['ir.attachment'].browse(attach_id)
                    if attach.name == 'product_data.xml':
                        old_product_xml = attach.datas
                        if product_xml != old_product_xml:
                            attach.unlink()
                            write_new_file = True
            else:
                write_new_file = True

            if write_new_file:
                # Create the xml attachment
                self.env['ir.attachment'].create({
                    'name': 'product_data.xml',
                    'datas_fname': 'product_data.xml',
                    'type': 'binary',
                    'datas': product_xml,
                    'res_model': 'product.template',
                    'res_id': self.id,
                    'mimetype': 'application/xml'
                })

                # Since the data changed set the last data change date
                self.write({
                    'data_last_change_date': datetime.now()
                })

        except Exception as e:
            error_text = '<p>Technical Errors, contact IT:' + '<p>'
            self.write({
                'data_errors': error_text + traceback.format_exc()
            })
            print(str(e))


class ProductCategory(models.Model):
    _inherit = 'product.category'

    def get_parent_name(self):
        if self.parent_id:
            return self.parent_id.get_parent_name()
        else:
            return self.name
