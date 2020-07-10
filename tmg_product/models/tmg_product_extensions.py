# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime
import urllib.request
import json
import xml.etree.ElementTree as ET


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
    pms = fields.Boolean(string='PMS Available', help='Is Pantone color matching available for this product and decoration method',
                         required=True)
    full_color = fields.Boolean(string='Full Color Available', help='Is Full Colro decoration avaiable for this product and decoration method',
                                required=True)
    max_colors = fields.Integer(string='Maximum Decoration colors',
                                help='Maximum number of colors that can be used for this product and decoration method',
                                required=True)

    @api.depends('decoration_method_id')
    def _set_name(self):
        self.name = self.decoration_method_id.name


class ProductDecorationArea(models.Model):
    _name = 'product.template.decorationarea'
    _description = 'Product Decoration Area'

    name = fields.Char(string='Name', compute='_set_name')
    product_tmpl_id = fields.Many2one(comodel_name='product.template', string='Product Template', ondelete='restrict', required=True)
    decoration_area_id = fields.Many2one(comodel_name='product.template.attribute.value', string='Decoration Area', required=True)
    decoration_method_id = fields.Many2one(comodel_name='product.template.decorationmethod', string='Decoration Method', required=True)
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
            if decoarea.depth and decoarea.width:
                dimensions = "{width:.2f}\" x {height:.2f}\"".format(width=decoarea.width, height=decoarea.height)
            decoarea.dimensions = dimensions

    @api.depends('decoration_area_id', 'decoration_method_id')
    def _set_name(self):
        self.name = self.decoration_area_id.name % ", " % self.decoration_method_id.name

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
    decoration_method_ids = fields.Many2many(comodel_name='product.template.attribute.value', string='Decoration Methods')


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    decoration_method_ids = fields.One2many(comodel_name='product.template.decorationmethod', inverse_name='product_tmpl_id')
    decoration_area_ids = fields.One2many(comodel_name='product.template.decorationarea', inverse_name='product_tmpl_id')
    addl_charge_product_ids = fields.One2many(comodel_name='product.addl.charges', inverse_name='product_tmpl_id')

    @api.constrains('decoration_method_ids')
    def _check_deco_methods(self):

        if any(len(template.decoration_method_ids) != len(template.decoration_method_ids.mapped('decoration_method_id')) for template in self):
            raise ValidationError('You cannot have the same decoration method on multiple lines!')
        return True

    def _build_all_xml(self):
        # Get a list of all active products that can be sold
        products = self.env['product.template'].search([('active','=',True),('sale_ok','=',True),('type','=','product')])
        for product in products:
            product._build_std_xml()

    def _build_std_xml(self):
        # First we will build the standard XML for the product.
        product = ET.Element('product')
        ET.SubElement(product, "product_style_number").text(self.product_style_number)
        ET.SubElement(product, "product_name").text(self.name)
        # The name of the product's category is the product category. The name of the top category in the path
        # is the brand
        ET.SubElement(product, "brand_name").text(self.category_id.get_parent_name())
        ET.SubElement(product, "category_name").text(self.category_id.name)
        ET.SubElement(product, "website_description").text(self.website_description)
        ET.SubElement(product, "width").text(str(self.width))
        ET.SubElement(product, "height").text(str(self.height))
        ET.SubElement(product, "dimensions").text(self.dimensions)
        ET.SubElement(product, "depth").text(str(self.depth))
        ET.SubElement(product, "weight").text(str(self.weight))
        # Get the res.config.settings model. If not found assume pounds
        config = self.env['res.config.settings'].search()
        if not config:
            ET.SubElement(product, "weight_uom").text("LB")
        else:
            if config.product_weight_in_lbs == "1":
                ET.SubElement(product, "weight_uom").text("LB")
            else:
                ET.SubElement(product, "weight_uom").text("KG")
        ET.SubElement(product, "product_variant_count").text(str(self.product_variant_count))
        ET.SubElement(product, "primary_material").text(self.primary_material)
        ET.SubElement(product, "pricing_year").text(datetime.now().year)
        ET.SubElement(product, "market_introduction_date").text(self.market_introduction_date.strftime("%Y-%m-%d"))
        ET.SubElement(product, "data_last_change_date").text(self.data_last_change_date.strftime("%Y-%m-%d"))
        # Split the keywords for the product
        keyword_elem = ET.SubElement(product, "website_meta_keywords")
        keywords = self.website_meta_keywords.split(", ")
        for keyword in keywords:
            ET.SubElement(keyword_elem, "keyword").text(keyword)
        product_tags_elem = ET.SubElement(product, "product_tags")
        for tag in self.product_tags_ids:
            ET.SubElement(product_tags_elem).text(tag.name)
        # Website tags will be any e-commerce category with a parent of "Tags"
        website_tags_elem = ET.SubElement(product, "website_tags")
        for category in self.public_categ_ids:
            if category.parent_id.name == 'Tags':
                ET.SubElement(website_tags_elem, "website_tag").text(category.name)
        # Website categories will be any e-commerce category with a parent of "Category".  This will also establish
        # the link between our website category and ASI/SAGE category.
        website_cats_elem = ET.SubElement(product, "product_categories")
        for category in self.public_categ_ids:
            if category.parent_id.name == "Category":
                website_cat_elem = ET.SubElement(website_cats_elem, "product_category")
                ET.SubElement(website_cat_elem, "name").text(category.name)
                ET.SubElement(website_cat_elem, "sage_category").text(category.sage_category_id.name)
                ET.SubElement(website_cat_elem, "asi_category").text(category.asi_category_id.name)
        alt_products_elem = ET.SubElement(product, "alternative_products")
        for product in self.alternative_product_ids:
            ET.SubElement(alt_products_elem, "alternative_product").text(product.product_style_number)
        warehouses_elem = ET.SubElement(product, "warehouses")
        for warehouse in self.warehouses:
            warehouse_elem = ET.SubElement(warehouses_elem, "warehouse")
            ET.SubElement(warehouse_elem, "name").text(warehouse.name)
            ET.SubElement(warehouse_elem, "zip").text(warehouse.partner_id.zip)
            ET.SubElement(warehouse_elem, "city").text(warehouse.partner_id.city)
            ET.SubElement(warehouse_elem, "state").text(warehouse.partner_id.state_id.code)
            ET.SubElement(warehouse_elem, "country").text(warehouse.partner_id.country_id.name)
            ET.SubElement(warehouse_elem, "code").text(warehouse.code)
        pvs_elem = ET.SubElement(product, "product_variants")
        # If the product has variants then add those.
        if self.product_variant_ids:
            # Loop through the product.products and add variant specific information
            for variant in self.product_variant_ids:
                pv_elem = ET.SubElement(pvs_elem, "product_variant")
                ET.SubElement(pv_elem, "product_variant_number").text(variant.default_code)
                ET.SubElement(pv_elem, "product_variant_name").text(variant.name)
                # Here we'll write the first attribute value that has a category of 'color' or 'thickness'
                for attribute_value in variant.attribute_value_ids:
                    if attribute_value.attribute_id.category in ('color','thickness'):
                        ET.SubElement(pv_elem, "product_variant_swatch").text(attribute_value.html_color)
                        ET.SubElement(pv_elem, "product_variant_color").text(attribute_value.name)
                        break
                # Write the packaging information for this product variant. We will only write out the first packaging
                # row
                if variant.packaging_ids:
                    pkg_elem = ET.SubElement(pv_elem, "packaging")
                    ET.SubElement(pkg_elem, "name").text(variant.packaging_ids[0].name)
                    ET.SubElement(pkg_elem, "qty").text(str(variant.packaging_ids[0].qty))
                    ET.SubElement(pkg_elem, "max_weight").text(str(variant.packaging_ids[0].max_weight))
                    ET.SubElement(pkg_elem, "length").text(str(variant.packaging_ids[0].weight))
                    ET.SubElement(pkg_elem, "width").text(str(variant.packaging_ids[0].width))
                    ET.SubElement(pkg_elem, "height").text(str(variant.packaging_ids[0].height))
                # Write the attributes that are specific to this variant (color, thickness, etc)
                attrs_elem = ET.SubElement(product, "attributes")
                for attribute_value in variant.attribute_value_ids:
                    attr_elem = ET.SubElement(attrs_elem, "attribute")
                    ET.SubElement(attr_elem, "attribute_category").text(attribute_value.attribute_id.category)
                    ET.SubElement(attr_elem, "attribute_id").text(str(attribute_value.id))
                    ET.SubElement(attr_elem, "attribute_sequence").text(str(attribute_value.sequence))






class ProductCategory(models.Model):
    _inherit = 'product.category'

    def get_parent_name(self):
        if self.parent_id:
            return self.parent_id._get_parent_name()
        else:
            return self.name

