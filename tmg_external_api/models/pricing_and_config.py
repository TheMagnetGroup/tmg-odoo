# -*- coding: utf-8 -*-

from odoo import models, api
import base64


class pricing_and_config(models.Model):
    _name = 'tmg_external_api.pricing_and_config'
    _description = 'Serve up product information on pricing and configuration'

# ------------------
#  Public functions
# ------------------

    @api.model
    def AvailableLocations(self, style_rqs):
        product_decoration_locations = dict(AvailableLocationArray=[],
                                            ErrorMessage=dict())

        if style_rqs:
            # make sure the product exists and is sellable
            sellable_product_ids = self.env['product.template'].get_product_saleable().ids
            product_search = [('product_style_number', '=', style_rqs),
                              ('id', 'in', sellable_product_ids)]
            product_decoration_locations = self._get_product_available_locations(product_search, style_rqs)
        else:
            product_decoration_locations = dict(ErrorMessage=dict(code=120,
                                                                  description="Product Style Number is required")
                                                )
        return product_decoration_locations

    @api.model
    def DecorationColors(self, style_rqs, location_rqs, decoration_rqs):
        decoration_colors = dict(DecorationColors=dict(),
                                 ErrorMessage=dict())

        if not style_rqs:
            decoration_colors = dict(
                ErrorMessage=dict(code=120,
                                  description="A valid product ID is required."))
        elif not location_rqs:
            decoration_colors = dict(
                ErrorMessage=dict(code=120,
                                  description="A valid product ID and location ID are both required"))
        else:
            sellable_product_ids = self.env['product.template'].get_product_saleable().ids
            pt_id_rqs = self.env['product.template'].search([('product_style_number', '=', style_rqs),
                                                             ('id', 'in', sellable_product_ids)]).ids
            if not pt_id_rqs:
                decoration_colors = dict(
                    ErrorMessage=dict(code=400,
                                      description=f"Product ID {style_rqs} not found or is not saleable"))
            else:
                product_colors_search = [('product_tmpl_id', '=', pt_id_rqs[0]),
                                         ('decoration_area_id', '=', location_rqs)]
                # load decoration_colors object(dictionary) if not already populated with an error message
                decoration_colors = self._get_product_decoration_colors(product_colors_search,
                                                                        style_rqs,
                                                                        location_rqs,
                                                                        decoration_rqs)
        return decoration_colors

    @api.model
    def FobPoints(self, style_rqs):
        fob_points_and_products = dict(FobPointArray=[],
                                       ErrorMessage=dict())

        sellable_product_ids = self.env['product.template'].get_product_saleable().ids
        fobs_with_products = self._get_sql_warehouses_and_products(style_rqs, sellable_product_ids)

        if fobs_with_products:
            fob_points = []
            fob_prod_list = []
            fob_processing = 0
            for fp in fobs_with_products:
                fob = fp[0]
                product_id = fp[1]
                if fob_processing != 0 and fob_processing != fob:
                    fob_points.append(self._load_warehouse_object(fob_processing, fob_prod_list))
                    fob_prod_list = []   # reset the list of products for processing the next fob
                fob_processing = fob
                fob_prod_list.append(dict(productId=product_id))
            # Load the warehouse data for the final fob point
            fob_points.append(self._load_warehouse_object(fob_processing, fob_prod_list))

            fob_points_and_products = dict(FobPointArray=fob_points,
                                           ErrorMessage=dict())
        elif style_rqs:
            product = self.env['product.template'].search([('product_style_number', '=', style_rqs),
                                                           ('id', 'in', sellable_product_ids)])
            if product[0]:
                fob_points_and_products = dict(
                    ErrorMessage=dict(code=403,
                                      description=f"Fob points not found for product {style_rqs}"))
            else:
                fob_points_and_products = dict(
                    ErrorMessage=dict(code=400,
                                      description=f"Product Data not found for product {style_rqs}"))
        else:
            fob_points_and_products = dict(
                ErrorMessage=dict(code=999,
                                  description="UNEXPECTEDLY NO warehouses/FOBs were found in the system at all"
                                          + " (the request for all FOB points for all products returned none)")
            )
        return fob_points_and_products

    @api.model
    def AvailableCharges(self, style_rqs):
        available_charges = dict(AvailableChargeArray=[],
                                 ErrorMessage=dict())

        sellable_product_ids = self.env['product.template'].get_product_saleable().ids
        product_search = [('id', 'in', sellable_product_ids)]
        if style_rqs:
            # make sure the product exists and is sellable
            product_search.append(('product_style_number', '=', style_rqs))

        available_charges = self._get_product_available_charges(product_search, style_rqs)

        return available_charges

    @api.model
    def ConfigurationAndPricing(self, style_rqs):
        export_config = dict()

        if style_rqs:
            # make sure the product exists and is sellable
            sellable_product_ids = self.env['product.template'].get_product_saleable().ids
            product_search = [('product_style_number', '=', style_rqs),
                              ('id', 'in', sellable_product_ids)]
            export_config = self._get_config_xml(product_search, style_rqs)
        else:
            export_config = dict(ErrorMessage=dict(code=120,
                                                   description="Product Style Number is required"))

        return export_config

# ------------------
#  Private functions
# ------------------

    def _get_product_available_locations(self, search, style):
        data = dict(AvailableLocationArray=[],
                    ErrorMessage=dict())
        product = self.env['product.template'].search(search).ids
        if product:
            available_locations = self.env['product.template.decorationarea']\
                .search_read([('product_tmpl_id', '=', product[0])], ['decoration_area_id'])
            for al in available_locations:
                # enter unique locations (by id)
                if len(data['AvailableLocationArray']) < 1 \
                        or (al['decoration_area_id'][0]
                            not in list({k['locationId']: k for k in data['AvailableLocationArray']}.keys())):
                    data['AvailableLocationArray'].append(dict(locationId=al['decoration_area_id'][0],
                                                               locationName=al['decoration_area_id'][1])
                                                          )
            if not data['AvailableLocationArray']:
                data = dict(ErrorMessage=dict(code=400,
                                              description=f"Available locations data not found for product {style}")
                            )
        else:
            data = dict(ErrorMessage=dict(code=400,
                                          description=f"Product ID {style} not found")
                        )
        return data

    def _get_product_decoration_colors(self, search, style, decoloco, decometh):
        data = dict(DecorationColors=dict(),
                    ErrorMessage=dict())
        errorcode = 0
        errormsg = ''
        product_locations_data = \
            self.env['product.template.decorationarea']\
                .search_read(search,
                             order='product_tmpl_id, decoration_area_id, decoration_method_id',
                             fields=['product_tmpl_id', 'decoration_area_id', 'decoration_method_id'])

        if product_locations_data:
            product_key = 0
            location_values = dict(ColorArray=[],
                                   productId='',
                                   locationId=0,
                                   DecorationMethodArray=[],
                                   pmsMatch=False,
                                   fullColor=False
                                   )
            # product_location_decorations_list = []
            for pld in product_locations_data:
                if decometh == 0 or pld['decoration_method_id'][0] == decometh:
                    decoration_and_colors = dict(decorationId=0,
                                                 decorationName='',
                                                 pms=False,
                                                 fullcolor=False,
                                                 colors=[]
                                                 )
                    # a/o ORIGINAL RELEASE (July 2021) the limit TO 1 PRODUCT/1 LOCATION MAKES THIS ROUTINE REDUNDANT
                    # # collect/accumulate location decoration/color data till a location-level break occurs
                    # if ((product_key != 0 and product_key != pld['product_tmpl_id'][0])
                    #     or (location_values['locationId'] != 0
                    #         and location_values['locationId'] != pld['decoration_area_id'][0])
                    # ):
                    #     location_values, product_location_decorations_list = \
                    #         self._apply_location_values(location_values, product_location_decorations_list)

                    product_key = pld['product_tmpl_id'][0]
                    # supply product_style_number as "productId" and load the collected location data
                    if style:
                        location_values['productId'] = style
                    else:
                        # otherwise obtain the style number from the product template ID
                        location_values['productId'] = \
                            self.env['product.template'].search_read([('id', '=', product_key)],
                                                                     ['product_style_number'])[0]['product_style_number']
                    location_values['locationId'] = pld['decoration_area_id'][0]

                    decoration_and_colors = self._get_decoration_color_data(pld['product_tmpl_id'][0],
                                                                            pld['decoration_method_id'][0])

                    if (len(location_values['DecorationMethodArray']) < 1
                            or
                            (decoration_and_colors['decorationId'] not in
                             list({k['decorationId']: k for k in location_values['DecorationMethodArray']}.keys()))
                    ):
                        location_values['DecorationMethodArray'].append(
                            dict(decorationId=decoration_and_colors['decorationId'],
                                 decorationName=decoration_and_colors['decorationName'])
                        )

                    if ((decoration_and_colors['fullcolor'])
                            or (decoration_and_colors
                                and decoration_and_colors['colors']
                                and len(decoration_and_colors['colors']) > 0)
                    ):

                        # availability for full color and pms match for a location will be considered "true" if any
                        # one single decoration for that location has "true".  Once set to true for a location
                        # do not allow any subsequent decoration to set it back to false at that same location level.
                        if not location_values['fullColor']:
                            location_values['fullColor'] = True if decoration_and_colors['fullcolor'] else False
                        if not location_values['pmsMatch']:
                            location_values['pmsMatch'] = True if decoration_and_colors['pms'] else False

                        for c in decoration_and_colors['colors']:
                            if (len(location_values['ColorArray']) < 1
                                or (c['colorId'] not in
                                    list({k['colorId']: k for k in location_values['ColorArray']}.keys()))
                            ):
                                location_values['ColorArray'].append(c)

            # a/o ORIGINAL RELEASE (July 2021) RESULT SET IS LIMITED TO 1 PRODUCT/1 LOCATION; THIS ROUTINE IS REDUNDANT
            # # after reading the final product/location data, append remaining location decoration data to the array
            # # location_values, product_location_decorations_list = \
            # #     self._apply_location_values(location_values, product_location_decorations_list)
            #
            # # return the list of products/locations/decorations/colors or begin error assessment
            # if product_location_decorations_list:
            #     data = dict(DecorationColors=product_location_decorations_list,
            #                 ErrorMessage=dict())
            if len(location_values['DecorationMethodArray']) < 1:
                # return error if no decoration methods, or else the single requested decoration method is not found
                if decometh:
                    errormsg = f'Decoration Method ID {str(decometh)}'
                else:
                    errormsg = 'Decoration Colors data'
            elif len(location_values['ColorArray']) > 0 or location_values['fullColor']:
                # return data if colors are found, or if no colors but a full-color process IS found
                data = dict(DecorationColors=location_values,
                            ErrorMessage=dict())
                errormsg = ''
            else:
                # return error if no color data or full-color process are found
                errormsg = 'Decoration Colors data'

        else:
            # otherwise return error if the specified location is not found
            errormsg = f'Location ID {str(decoloco)}'

        # if error message text was begun, complete the appropriate indications
        if errormsg:
            if decometh or decoloco or style:
                errorcode = 400    # use error 400 to represent "not found" for specified requests
                errormsg += ' was not found for the requested'
                if decometh:
                    errormsg += f' Decoration Method ID {str(decometh)}'
                if decoloco:
                    errormsg += f' Location ID {str(decoloco)}'
                if style:
                    errormsg += f' Product ID {style}'
            # a/o ORIGINAL RELEASE (July 2021) the limit to 1 PRODUCT/1 LOCATION MAKES THIS CONDITION REDUNDANT
            # else:
            #     errorcode = 999    # use error 999 to indicate an abnormal system condition of NO DATA found
            #     errormsg = ("UNEXPECTEDLY, NO Decoration Colors data was found AT ALL"
            #                 + " (request was for ALL decoration colors for ALL products)")
            data = dict(ErrorMessage=dict(code=errorcode,
                                          description=errormsg))

        return data

    # a/o ORIGINAL RELEASE (July 2021) RESULT SET IS LIMITED TO 1 PRODUCT WITH 1 LOCATION; THIS FUNCTION IS REDUNDANT
    # def _apply_location_values(self, location_values, location_decoration_color_list):
    #     """
    #     # this method is designed to be invoked only if the caller has a location-level break;
    #     # its purpose is to format the input parameter values as a decoration colors object and then load/append
    #     # that decoration colors object to the "location_decoration_color_list"
    #     :param location_values: dict() of the current location-level break accumulated values
    #     :param location_decoration_color_list: [] list of the products with corresponding location decoration colors
    #     :return: 1) reset and return the location-level break accumulators
    #              2) return the "location_decoration_color_list" whether the conditions determined that appending
    #                 data to this list is appropriate or not.
    #     """
    #
    #     # the product/location must be unique in the list, and there must exist decoration color data;
    #     # ...otherwise simply return the location_decoration_color_list unchanged as-is and reset level break values
    #     if (((location_values['productId'] not in
    #           list({k['productId']: k for k in location_decoration_color_list}.keys()))
    #          or (location_values['locationId']
    #              not in list({k['locationId']: k for k in location_decoration_color_list}.keys()))
    #         )
    #         and
    #         ((location_values['ColorArray'] and len(location_values['ColorArray']) > 0)
    #          and (location_values['DecorationMethodArray'] and len(location_values['DecorationMethodArray']) > 0)
    #         )
    #     ):
    #         location_decoration_color_list.append(location_values)
    #
    #     # reset the location-level break accumulators regardless of appended data or not
    #     location_values = dict(ColorArray=[],
    #                            productId='',
    #                            locationId=0,
    #                            DecorationMethodArray=[],
    #                            pmsMatch=False,
    #                            fullColor=False
    #                            )
    #     return location_values, location_decoration_color_list

    def _get_decoration_color_data(self, product_id, decometh_id):
        decoration_color_data = dict()
        decodata = self.env['product.template.decorationmethod']\
            .search_read([('product_tmpl_id', '=', product_id), ('decoration_method_id', '=', decometh_id)],
                         ['pms', 'full_color'])
        if decodata:
            deconame = self.env['product.attribute.value'].search_read([('id', '=', decometh_id)], ['name'])
            decoration_colors = self._get_applicable_colors('impcolor', product_id, decometh_id)

            decoration_color_data = dict(decorationId=decometh_id,
                                         decorationName=deconame[0]['name'],
                                         pms=decodata[0]['pms'],
                                         fullcolor=decodata[0]['full_color'],
                                         colors=decoration_colors
                                         )

        return decoration_color_data

    def _get_applicable_colors(self, attribute_category_name, product, decoration):
        applicable_colors = []
        color = dict(colorId=0,
                     colorName="")

        # obtain the attribute ID that corresponds to the category/attribute name for decoration imprint colors
        imprint_colors_attribute_id = \
            self.env['product.attribute'].search([('category', '=', attribute_category_name)]).ids[0]

        # obtain the decoration color ids associated with the product template attribute line
        product_decoration_color_ids = self.env['product.template.attribute.line'] \
            .search_read([('product_tmpl_id', '=', product),
                          ('attribute_id', '=', imprint_colors_attribute_id)],
                         ['value_ids'])
        # obtain decoration color data for the ids and appropriately rename/reformat for Promostandards color array
        product_decoration_color_list = []
        if product_decoration_color_ids:
            product_decoration_color_list = \
                self.env['product.attribute.value']\
                    .search_read([('id', 'in', product_decoration_color_ids[0]['value_ids'])], ['id', 'name'])
        # # obtain the list of color exclusions that apply to the current product and decoration
        # product_decoration_color_exclusions = self._get_sql_color_exclusions(product, decoration)
        #
        # # filter the colors by exclusion to leave only the ones that apply to the current decoration method
        # for dcx in decoration_colors_category_color_list:
        #     if dcx['id'] not in list({k[0]: k for k in product_decoration_color_exclusions}.keys()):
        #         color = dict(colorId=dcx['id'],
        #                      colorName=dcx['name'])
        #         applicable_colors.append(color)
        for pdc in product_decoration_color_list:
            color = dict(colorId=pdc['id'],
                         colorName=pdc['name'])
            applicable_colors.append(color)

        return applicable_colors

    # def _get_sql_color_exclusions(self, product, decoration):
    #     """
    #     # because of the somewhat complex task of joining to product.template.attribute twice, once for 1) obtaining
    #     # the exclusion list ID that applies to the specific decoration method, and then again for 2) obtaining the
    #     # actual color IDs associated with that list that are to be excluded from that decoration method, I utilized
    #     # direct SQL access via postgreSQL.
    #     :param product:
    #     :param decoration:
    #     :return: [] list of decoration colors to be excluded from the current decoration for this product
    #     """
    #     sql = f"""select tv.product_attribute_value_id
    #                 from product_template_attribute_value tv
    #                      inner
    #                 join product_attr_exclusion_value_ids_rel xv
    #                   on tv.id = xv.product_template_attribute_value_id
    #                      inner
    #                 join product_template_attribute_exclusion ax
    #                   on tv.product_tmpl_id = ax.product_tmpl_id
    #                  and xv.product_template_attribute_exclusion_id = ax.id
    #                      inner
    #                 join product_template_attribute_value xt
    #                   on ax.product_template_attribute_value_id = xt.id
    #                  and ax.product_tmpl_id = xt.product_tmpl_id
    #                where tv.product_tmpl_id = {product}
    #                  and xt.product_attribute_value_id = {decoration}"""
    #     self.env.cr.execute(sql)
    #     color_exclusions = self.env.cr.fetchall()
    #
    #     return color_exclusions

    def _get_sql_warehouses_and_products(self, style, sellables):
        sql = f"""select sw.stock_warehouse_id, pt.product_style_number
                   from product_template_stock_warehouse_rel sw
                        inner
                   join product_template pt on sw.product_template_id = pt.id
                  where sw.product_template_id in {tuple(sellables)} """
        # a/o 2021-04-01 if style# is specified, the list of products will instead be limited to that product alone,
        # as was currently the convention for returning the Magnet/Brands FOB points requests in the .NET API code.
        if style:
            sql += f""" and pt.product_style_number = '{style}' """

        # append the order-by sequencing clause to effectively group the product list by warehouses
        sql += """ order by stock_warehouse_id, product_style_number;"""

        self.env.cr.execute(sql)
        whse_and_products = self.env.cr.fetchall()
        return whse_and_products

    def _load_warehouse_object(self, fob, products):
        warehouse = self.env['stock.warehouse'].search_read([('id', '=', fob)], ['name', 'partner_id'])
        w_address = self.env['res.partner'].search_read([('id', '=', warehouse[0]['partner_id'][0])],
                                                        ['city', 'zip', 'state_id', 'country_id'])
        data = dict(fobId=warehouse[0]['name'],
                    fobPostalCode=w_address[0]['zip'],
                    fobCity=w_address[0]['city'],
                    fobState=self.env['res.country.state'].search([('id',
                                                                    '=',
                                                                    w_address[0]['state_id'][0])]).code,
                    fobCountry=self.env['res.country'].search([('id',
                                                                '=',
                                                                w_address[0]['country_id'][0])]).code,
                    CurrencySupportedArray=[dict(currency="USD")],
                    ProductArray=sorted(products, key=lambda k: k['productId']))
        # NOTE: a/o 2021-06-02 USD is the only supported currency
        return data

    def _get_product_available_charges(self, search, style):
        data = dict(AvailableChargeArray=[],
                    ErrorMessage=dict())
        products = self.env['product.template'].search(search).ids
        if products:
            chgs_list = []
            addl_charges = self.env['product.addl.charges']\
                .search_read([('product_tmpl_id', '=', products[0])], ['addl_charge_product_id', 'charge_type'])
            for ac in addl_charges:
                # enter unique charges (by id)
                if len(chgs_list) < 1 or (ac['id'] not in list({k['chargeId']: k for k in chgs_list}.keys())):
                    chg_desc = self.env['product.template'].search_read([('id', '=', ac['addl_charge_product_id'][0])],
                                                                        ['name', 'default_code'])
                    chgs_list.append(dict(chargeId=ac['id'],
                                     chargeName=chg_desc[0]['default_code'],
                                     chargeType=ac['charge_type'],
                                     chargeDescription=chg_desc[0]['name'])
                                     )
            if chgs_list:
                data = dict(AvailableChargeArray=chgs_list,
                            ErrorMessage=dict())
            elif style:
                data = dict(ErrorMessage=dict(code=400,
                                              description=f"Available charges data not found for product {style}")
                            )
            else:
                data = dict(
                    ErrorMessage=dict(code=999,
                                      description="UNEXPECTEDLY, no available charges were found in the system at all"
                                           + " (the request for all available charges for all products returned none)")
                )
        elif style:
            data = dict(ErrorMessage=dict(code=400,
                                          description=f"Product ID {style} not found")
                        )

        return data

    def _get_config_xml(self, item_search, style):
        product_config_data = dict()
        stored_xml_64 = None
        export_account_name = 'PSPricingAndConfiguration'

        # assemble the export file name, compiled from segments of the PricingAndConfig export account attributes
        stored_pricing_and_config_file = self.env['tmg_external_api.tmg_export_account'] \
            .search_read([('name', '=', export_account_name)], ['category', 'name', 'file_extension'])
        if stored_pricing_and_config_file:
            export_file_name = "product_data_{}_{}.{}".format(stored_pricing_and_config_file[0]['category'],
                                                              stored_pricing_and_config_file[0]['name'],
                                                              stored_pricing_and_config_file[0]['file_extension'])

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
                    product_config_xml_str = base64.b64decode(stored_xml_64.datas).decode("utf-8")
                    product_config_data = dict(xmlString=product_config_xml_str.replace("\n", ""),
                                               ErrorMessage=dict())
                else:
                    product_config_data = dict(
                        ErrorMessage=dict(code=999,
                                          description="Pricing and Configuration XML data was expected but NOT found")
                    )
            else:
                product_config_data = dict(
                    ErrorMessage=dict(code=400,
                                      description=f'Product ID "{style}" not found')
                )
        else:
            product_config_data = dict(
                ErrorMessage=dict(code=999,
                                  description=f'Product Export Account "{export_account_name}" record is missing')
            )

        return product_config_data
