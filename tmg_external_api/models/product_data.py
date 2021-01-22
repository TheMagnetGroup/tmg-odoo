# -*- coding: utf-8 -*-

from odoo import models, fields, api
import base64


class product_data(models.Model):
    _name = 'tmg_external_api.product_data'
    _description = 'Serve up product information by item/variants, as list of sellables, or list of closeouts'

# ------------------
#  Public functions
# ------------------

    @api.model
    def ProductSellable(self, style_rqs, variant_rqs):

        sellable_product_ids = self.env['product.template'].get_product_saleable().ids
        search_for_sellable = [('product_tmpl_id', 'in', sellable_product_ids)]
        if style_rqs:
            search_for_sellable.append(('product_style_number', '=', style_rqs))
        elif variant_rqs:
            return [dict(errorOdoo=dict(code=120,
                                        message="If Variant number is requested, Style is also required"))]

        product_sellable_export = self._get_sellable_products(search_for_sellable, variant_rqs)
        return product_sellable_export

    @api.model
    def ProductCloseout(self):
        # determine closeout status from sellable products that are categorized "discontinued"
        sellable_product_ids = self.env['product.template'].get_product_saleable().ids
        category_discontinued_ids = \
            self.env['product.category'].search([('complete_name', 'ilike', 'discontinued')]).ids
        search_for_closeouts = [('product_tmpl_id', 'in', sellable_product_ids),
                                ('product_tmpl_id.categ_id', 'in', category_discontinued_ids)]

        product_closeout_export = self._get_closeout_products(search_for_closeouts)

        return product_closeout_export

    @api.model
    def ProductData(self, style_rqs):
        product_export = dict()

        if style_rqs:
            # make sure the product exists and is sellable
            sellable_product_ids = self.env['product.template'].get_product_saleable().ids
            product_search = [('product_style_number', '=', style_rqs),
                              ('id', 'in', sellable_product_ids)]
            product_export = self._get_product_stored_xml(product_search, style_rqs)
        else:
            product_export = dict(
                errorOdoo=dict(code=120,
                               message="Product Style Number is required")
            )

        return product_export

    @api.model
    def ProductDateModified(self, change_as_of_date_str):
        product_date_modified_export = dict()

        if change_as_of_date_str and change_as_of_date_str.strip():
            sellable_product_ids = self.env['product.template'].get_product_saleable().ids
            change_as_of_date = fields.Datetime.from_string(change_as_of_date_str)
            date_modified_search = [('data_last_change_date', '>=', change_as_of_date),
                                    ('product_tmpl_id', 'in', sellable_product_ids)]
            product_date_modified_export = self._get_date_modified_products(date_modified_search,
                                                                            change_as_of_date_str)
        else:
            product_date_modified_export = dict(
                errorOdoo=dict(code=120,
                               message="Product Last Changed timestamp is required")
            )

        return product_date_modified_export

# ------------------
#  Private functions
# ------------------

    def _get_sellable_products(self, search, variant):
        sellable_products = []
        sellable_list = self.env['product.product'].search_read(search, ['product_style_number', 'default_code'])
        for s in sellable_list:
            if not variant or s['default_code'] == variant:
                data = dict(errorOdoo=dict(),
                            styleNumber=s['product_style_number'],
                            productVariant=s['default_code'])
                sellable_products.append(data)
        if len(sellable_products) == 0:
            if len(sellable_list) == 0:
                # not even the main product was found
                sellable_products = [
                    dict(errorOdoo=dict(code=130,
                                        message="No sellable product data found (only sellable data is returned)"))]
            else:
                # variants were found but none matched the request
                sellable_products = [
                    dict(errorOdoo=dict(code=140,
                                        message="Product " + sellable_list[0]['product_style_number']
                                                + " has no variant that matches '" + variant + "'"))]

        return sellable_products

    def _get_closeout_products(self, search):
        closeout_products = []
        closeouts = self.env['product.product'].search_read(search, ['product_style_number', 'default_code'])
        for co in closeouts:
            data = dict(errorOdoo=dict(),
                        styleNumber=co['product_style_number'],
                        productVariant=co['default_code'])
            closeout_products.append(data)
        if len(closeout_products) == 0:
            closeout_products = [
                dict(errorOdoo=dict(code=130,
                                    message="No closeout product data was found")
                     )]

        return closeout_products

    def _get_product_stored_xml(self, item_search, style):
        stored_export = dict()
        stored_xml_64 = None
        export_account_name = 'PSProductData'

        # assemble the export file name, compiled from segments of the ProductData export account attributes
        product_data_export_account = self.env['tmg_external_api.tmg_export_account'] \
            .search_read([('name', '=', export_account_name)], ['category', 'name', 'file_extension'])
        if product_data_export_account:
            export_file_name = "product_data_{}_{}.{}".format(product_data_export_account[0]['category'],
                                                              product_data_export_account[0]['name'],
                                                              product_data_export_account[0]['file_extension'])

            # obtain the product-specific instance of the product.template model via item search by style number
            product_obj_list = self.env['product.template']
            item_list = product_obj_list.search(item_search)

            if item_list:
                item = item_list[0]
                # Get the attachment ID(s) based on the ID of the product style
                attachment_ids = self.env['ir.attachment'].search([('res_id', '=', item['id']),
                                                                   ('name', '=', export_file_name),
                                                                   ('res_model', '=', 'product.template')]).ids
                # Ignore files that are from mail_thread of the product
                message_attachment_ids = item_list.mapped('message_ids.attachment_ids').ids
                attachment_ids = list(set(attachment_ids) - set(message_attachment_ids))
                if len(attachment_ids) > 0:
                    stored_xml_64 = self.env['ir.attachment'].browse(attachment_ids[0])

                if stored_xml_64:
                    # Odoo stores large data (e.g. images) in base64 so decode to bytes, then decode bytes to a string
                    product_xml_str = base64.b64decode(stored_xml_64.datas).decode("utf-8")
                    stored_export = dict(errorOdoo=dict(),
                                         xmlString=product_xml_str.replace("\n", ""))
                else:
                    stored_export = dict(odooError=dict(code=999,
                                                        message="Product XML data was expected but NOT found"))

            else:
                stored_export = dict(odooError=dict(code=130,
                                                    message="Product '" + style + "' not found"))

        else:
            stored_export = dict(odooError=dict(code=999,
                                                message='Product Export Account "' + export_account_name
                                                        + '" record is missing'))

        return stored_export

    def _get_date_modified_products(self, search, as_of_date_str):
        date_modified_products = []
        mod_prods = self.env['product.product'].search_read(search, ['product_style_number', 'default_code'])
        for mp in mod_prods:
            data = dict(errorOdoo=dict(),
                        styleNumber=mp['product_style_number'],
                        productVariant=mp['default_code'])
            date_modified_products.append(data)
        if len(date_modified_products) == 0:
            date_modified_products = [
                dict(errorOdoo=dict(code=130,
                                    message="No product data found that was modified since " + as_of_date_str)
                     )]
        return date_modified_products
