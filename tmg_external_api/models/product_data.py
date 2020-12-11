# -*- coding: utf-8 -*-

from odoo import models, api
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

        closeout_cursor = self._get_closeouts_sql()
        closeout_product_ids = closeout_cursor.fetchall()

        closeouts_search = [('product_tmpl_id', 'in', closeout_product_ids)]
        product_closeout_export = self._get_closeout_products(closeouts_search)

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

    def _get_closeouts_sql(self):
        # filter the list of sellable product ids for only closeout products
        sellable_product_ids = self.env['product.template'].get_product_saleable().ids
        sql = """select product_template_id
                   from product_template_product_template_tags_rel
                  where product_template_tags_id 
                        in (select id from product_template_tags where name = %(TagName)s)
                    and product_template_id
                        in %(SellableProducts)s;"""
        params = {'TagName': 'Closeout',
                  'SellableProducts': tuple(sellable_product_ids)}
        cursor = self.env.cr
        cursor.execute(sql, params)
        return cursor

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
