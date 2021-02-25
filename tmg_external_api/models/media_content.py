# -*- coding: utf-8 -*-

from odoo import models, fields, api
import base64


class media_content(models.Model):
    _name = 'tmg_external_api.media_content'
    _description = 'Serve up product media information by item/variants or list of modified as-of specified date'

# ------------------
#  Public functions
# ------------------
    @api.model
    def MediaContent(self, style_rqs):
        product_export = dict()

        if style_rqs:
            # make sure the product exists and is sellable
            sellable_product_ids = self.env['product.template'].get_product_saleable().ids
            product_search = [('product_style_number', '=', style_rqs),
                              ('id', 'in', sellable_product_ids)]
            product_export = self._get_media_stored_xml(product_search, style_rqs)
        else:
            product_export = dict(errorOdoo=dict(code=120,
                                                 message="Product Style Number is required"))

        return product_export

    @api.model
    def MediaContentDateModified(self, change_as_of_date_str):
        media_date_modified_export = dict()

        if change_as_of_date_str and change_as_of_date_str.strip():
            sellable_product_ids = self.env['product.template'].get_product_saleable().ids
            change_as_of_date = fields.Datetime.from_string(change_as_of_date_str)
            date_modified_search = [('image_last_change_date', '>=', change_as_of_date),
                                    ('product_tmpl_id', 'in', sellable_product_ids)]
            media_date_modified_export = self._get_date_modified_media(date_modified_search,
                                                                       change_as_of_date_str)
        else:
            media_date_modified_export = dict(
                errorOdoo=dict(code=120,
                               message="Media Last Changed timestamp is required")
            )

        return media_date_modified_export

# ------------------
#  Private functions
# ------------------

    def _get_media_stored_xml(self, item_search, style):
        stored_export = dict()
        stored_xml_64 = None
        export_account_name = 'PSMediaContent'
        # assemble the export file name, compiled from segments of the ProductData export account attributes
        media_content_export_account = self.env['tmg_external_api.tmg_export_account'] \
            .search_read([('name', '=', export_account_name)], ['category', 'name', 'file_extension'])
        if media_content_export_account:
            export_file_name = "product_data_{}_{}.{}".format(media_content_export_account[0]['category'],
                                                              media_content_export_account[0]['name'],
                                                              media_content_export_account[0]['file_extension'])
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
                    stored_export = dict(errorOdoo=dict(code=160,
                                                        message="No media content data found"))
            else:
                stored_export = dict(errorOdoo=dict(code=130,
                                                    message="Product '" + style + "' not found"))
        else:
            stored_export = dict(errorOdoo=dict(code=999,
                                                message='Product Export Account "' + export_account_name
                                                        + '" record is missing'))
        return stored_export

    def _get_date_modified_media(self, search, as_of_date_str):
        date_modified_media = []
        mod_media = self.env['product.product'].search_read(search, ['product_style_number', 'default_code'])
        for mp in mod_media:
            data = dict(errorOdoo=dict(),
                        styleNumber=mp['product_style_number'],
                        productVariant=mp['default_code'])
            date_modified_media.append(data)
        if len(date_modified_media) == 0:
            date_modified_media = [
                dict(errorOdoo=dict(code=130,
                                    message="No media content data found that was modified since " + as_of_date_str)
                     )]
        return date_modified_media
