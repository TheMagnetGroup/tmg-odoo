# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, datetime
import json


class promostandards(models.Model):
    _name = 'tmg_external_api.promostandards'

    name = fields.Char(string="API Name")

    debug = fields.Boolean(string="Debug Mode")



    @api.multi
    def get_partner(self, partner_id):
        if not partner_id:
            return False
        partner_obj = self.env['res.partner']
        partner = partner_obj.browse(int(partner_id))
        return partner

    @api.multi
    def get_api(self, api_name):
        api_container = self.env['tmg_external_api.promostandards']
        apiID = api_container.search([('name', '=', api_name)])
        return apiID

    @api.multi
    def check_call_cap(self, partner_id):
        partner = self.get_partner(partner_id)
        if partner.current_call_count + 1 > partner.daily_call_cap:
            return False
        else:
            return True

    @api.multi
    def _check_debug(self, partner_id, api_name):
        partner = self.get_partner(partner_id)
        api = self.get_api(api_name)
        if api.debug or partner.debug:
            return True
        else:
            return False

    @api.multi
    def log_transaction(self, partner_id, request, api_name):
        partner = self.get_partner(partner_id)
        partner.current_call_count += 1
        if self._check_debug(partner_id, api_name):
            log_obj = self.env['tmg_external_api.api_logging']
            new_log = log_obj.create({
                'api_name': api_name,
                'partner_id': partner_id,
                'request': request
            })
        return True

    # Test function for call cap
    @api.multi
    def test_button(self):
        # test = self.OrderStatus("","SO4043","01-01-2000",'3326', "fjfj")
        test = self.ship_notification('','','01-01-2020', '20548', '')

    def ship_notification(self, PONumber, SONumber, Ship, Partner_id, Request):
        if not self.check_call_cap(Partner_id):
            data = [('Error', '=', "Call Cap")]
            return data
        soCont = self.env['tmg_external_api.shipment_notificaiton']
        data = soCont.ShipmentNotification(PONumber, SONumber,Ship,Partner_id)
        self.log_transaction(Partner_id, Request, "Shipment Notification")
        return data


    def shipments(self):
        soCont = self.env['sale.order']
        apiID = soCont.search([('name', '=', 'SO016')])
        shipObj = self.env['tmg_external_api.shipment_notificaiton']
        shipObj.get_common_shipments(apiID.picking_ids)
    @api.multi
    def OrderStatus(self, PONumber, SONumber, LastUpdate, Partner_id, Request):
        if not self.check_call_cap(Partner_id):
            data = [('Error', '=', "Call Cap") ]
            return data


        statusObj = self.env['tmg_external_api.order_status']
        data = statusObj.OrderStatus(PONumber, SONumber,LastUpdate,Partner_id)
        self.log_transaction(Partner_id,Request,"Order Status")
        return data

    @api.model
    def Inventory(self, style_rqs, colors_rqs, partner_id, request):
        if not self.check_call_cap(partner_id):
            data = [('Error', '=', "Call Cap")]
            return data
        inventory_obj = self.env['tmg_external_api.inventory']
        data = inventory_obj.Inventory(style_rqs, colors_rqs)
        self.log_transaction(partner_id, request, "Inventory")
        return data

    @api.model
    def InventoryFilterValues(self, style_rqs, partner_id, request):
        if not self.check_call_cap(partner_id):
            data = [('Error', '=', "Call Cap")]
            return data
        inventory_obj = self.env['tmg_external_api.inventory']
        data = inventory_obj.InventoryFilterValues(style_rqs)
        self.log_transaction(partner_id, request, "Inventory Filter Values")
        return data

    @api.model
    def Invoice(self, partner_str, po, invoice_number, invoice_date_str, as_of_date_str, request):
        if not partner_str or not partner_str.strip():
            data = [dict(
                        errorList=[dict(
                            code=100,
                            severity="Error",
                            message="Invalid partner ID value: '" + partner_str + "'")
                            ]
                        )
                    ]
            return data
        elif not self.check_call_cap(partner_str):
            data = [dict(
                        errorList=[dict(
                            code=999,
                            severity="Error",
                            message="Call Cap not found for partner ID " + partner_str)
                            ]
                        )
                    ]
            return data
        invoice_obj = self.env['tmg_external_api.invoice']
        data = invoice_obj.Invoice(partner_str, po, invoice_number, invoice_date_str, as_of_date_str)
        self.log_transaction(partner_str, request, "Invoice")
        return data

    @api.model
    def ProductSellable(self, partner_str, style_rqs, variant_rqs, request):
        if not partner_str or not partner_str.strip():
            data = [dict(errorOdoo=dict(code=100,
                                        message="Invalid partner ID value: '" + partner_str + "'"))]
            return data
        elif not self.check_call_cap(partner_str):
            data = [dict(errorOdoo=dict(code=999,
                                        message="Call Cap not found for partner ID " + partner_str))]
            return data
        sellables_obj = self.env['tmg_external_api.product_data']
        data = sellables_obj.ProductSellable(style_rqs, variant_rqs)
        self.log_transaction(partner_str, request, "ProductSellable")
        return data

    @api.model
    def ProductCloseout(self, partner_str, request):
        if not partner_str or not partner_str.strip():
            data = [dict(errorOdoo=dict(code=100,
                                        message="Invalid partner ID value: '" + partner_str + "'"))]
            return data
        elif not self.check_call_cap(partner_str):
            data = [dict(errorOdoo=dict(code=999,
                                        message="Call Cap not found for partner ID " + partner_str))]
        closeouts_obj = self.env['tmg_external_api.product_data']
        data = closeouts_obj.ProductCloseout()
        self.log_transaction(partner_str, request, "ProductCloseout")
        return data

    @api.model
    def ProductData(self, partner_str, style_rqs, request):
        if not partner_str or not partner_str.strip():
            data = [dict(errorOdoo=dict(code=100,
                                        message="Invalid partner ID value: '" + partner_str + "'"))]
            return data
        elif not self.check_call_cap(partner_str):
            data = [dict(errorOdoo=dict(code=999,
                                        message="Call Cap not found for partner ID " + partner_str))]
            return data
        product_data_obj = self.env['tmg_external_api.product_data']
        data = product_data_obj.ProductData(style_rqs)
        self.log_transaction(partner_str, request, "ProductData")
        return data

    @api.model
    def ProductDateModified(self, partner_str, as_of_date_str, request):
        if not partner_str or not partner_str.strip():
            data = [dict(errorOdoo=dict(code=100,
                                        message="Invalid partner ID value: '" + partner_str + "'"))]
            return data
        elif not self.check_call_cap(partner_str):
            data = [dict(errorOdoo=dict(code=999,
                                        message="Call Cap not found for partner ID " + partner_str))]
        modified_products_obj = self.env['tmg_external_api.product_data']
        data = modified_products_obj.ProductDateModified(as_of_date_str)
        self.log_transaction(partner_str, request, "ProductDateModified")
        return data

    @api.model
    def MediaContent(self, partner_str, style_rqs, request):
        if not partner_str or not partner_str.strip():
            data = [dict(errorList=[dict(
                            code=100,
                            message="Invalid partner ID value: '" + partner_str + "'")
                            ]
                         )]
            return data
        elif not self.check_call_cap(partner_str):
            data = [dict(errorList=[dict(
                            code=999,
                            message="Call Cap not found for partner ID " + partner_str)
                            ]
                         )]
            return data
        media_content_obj = self.env['tmg_external_api.media_content']
        data = media_content_obj.MediaContent(style_rqs)
        self.log_transaction(partner_str, request, "MediaContent")
        return data

    @api.model
    def MediaContentDateModified(self, partner_str, as_of_date_str, request):
        if not partner_str or not partner_str.strip():
            data = [dict(errorOdoo=dict(code=100,
                                        message="Invalid partner ID value: '" + partner_str + "'"))]
            return data
        elif not self.check_call_cap(partner_str):
            data = [dict(errorOdoo=dict(code=999,
                                        message="Call Cap not found for partner ID " + partner_str))]
        modified_products_obj = self.env['tmg_external_api.media_content']
        data = modified_products_obj.MediaContentDateModified(as_of_date_str)
        self.log_transaction(partner_str, request, "MediaContentDateModified")
        return data

    @api.model
    def AvailableLocations(self, partner_str, style_rqs, request):
        locations_dict = dict()
        if not partner_str or not partner_str.strip():
            locations_dict = dict(ErrorMessage=dict(code=100,
                                                    description="Invalid partner ID value: '" + partner_str + "'"))
            return locations_dict
        elif not self.check_call_cap(partner_str):
            locations_dict = dict(ErrorMessage=dict(code=999,
                                                    description="Call Cap not found for partner ID " + partner_str))
            return locations_dict
        locations_obj = self.env['tmg_external_api.pricing_and_config']
        locations_dict = locations_obj.AvailableLocations(style_rqs)
        self.log_transaction(partner_str, request, "AvailableLocations")
        return locations_dict

    @api.model
    def DecorationColors(self, partner_str, style_rqs, location_rqs, decoration_rqs, request):
        decoration_colors_dict = dict()
        if not partner_str or not partner_str.strip():
            decoration_colors_dict = dict(
                ErrorMessage=dict(code=100,
                                  description="Invalid partner ID value: '" + partner_str + "'"))
            return decoration_colors_dict
        elif not self.check_call_cap(partner_str):
            decoration_colors_dict = dict(
                ErrorMessage=dict(code=999,
                                  description="Call Cap not found for partner ID " + partner_str))
            return decoration_colors_dict
        decoration_colors_obj = self.env['tmg_external_api.pricing_and_config']
        decoration_colors_dict = decoration_colors_obj.DecorationColors(style_rqs, location_rqs, decoration_rqs)
        self.log_transaction(partner_str, request, "DecorationColors")
        return decoration_colors_dict

    @api.model
    def FobPoints(self, partner_str, style_rqs, request):
        fob_dict = dict()
        if not partner_str or not partner_str.strip():
            fob_dict = dict(ErrorMessage=dict(code=100,
                                              description="Invalid partner ID value: '" + partner_str + "'"))
            return fob_dict
        elif not self.check_call_cap(partner_str):
            fob_dict = dict(ErrorMessage=dict(code=999,
                                              description="Call Cap not found for partner ID " + partner_str))
            return fob_dict
        fob_points_obj = self.env['tmg_external_api.pricing_and_config']
        fob_dict = fob_points_obj.FobPoints(style_rqs)
        self.log_transaction(partner_str, request, "FobPoints")
        return fob_dict

    @api.model
    def AvailableCharges(self, partner_str, style_rqs, request):
        charges_dict = dict()
        if not partner_str or not partner_str.strip():
            charges_dict = dict(ErrorMessage=dict(code=100,
                                                  description="Invalid partner ID value: '" + partner_str + "'"))
            return charges_dict
        elif not self.check_call_cap(partner_str):
            charges_dict = dict(ErrorMessage=dict(code=999,
                                                  description="Call Cap not found for partner ID " + partner_str))
            return charges_dict
        charges_obj = self.env['tmg_external_api.pricing_and_config']
        charges_dict = charges_obj.AvailableCharges(style_rqs)
        self.log_transaction(partner_str, request, "AvailableCharges")
        return charges_dict

    @api.model
    def ConfigurationAndPricing(self, partner_str, style_rqs, pricing_rqs, config_rqs, request):
        if not partner_str or not partner_str.strip():
            data = [dict(ErrorMessage=dict(code=100,
                                           description="Invalid partner ID value: '" + partner_str + "'"))]
            return data
        elif not self.check_call_cap(partner_str):
            data = [dict(ErrorMessage=dict(code=999,
                                           description="Call Cap not found for partner ID " + partner_str))]
            return data
        config_obj = self.env['tmg_external_api.pricing_and_config']
        data = config_obj.ConfigurationAndPricing(partner_str, style_rqs, pricing_rqs, config_rqs)
        self.log_transaction(partner_str, request, "ConfigurationAndPricing")
        return data

    # def OrderStatus(self, PONumber, SONumber, LastUpdate, Partner_id):
    #     if LastUpdate == '':
    #         LastUpdate = '02/01/1990'
    #     sql = """SELECT sale.id
    #                 FROM sale_order as sale
    #                 join res_partner partner ON (partner.id = sale.partner_id)
    #                 where (client_order_ref = %(PONumber)s or %(PONumber)s =  '')
    #                 and (CAST(partner.id as VARCHAR(20)) = %(Partner_ID)s or %(Partner_ID)s = '')
    #                 and (sale.name = %(SONumber)s or %(SONumber)s = '')
    #                 and (sale.write_date >= %(LastUpdate)s);"""
    #     params = {
    #         'PONumber': PONumber,
    #         'SONumber': SONumber,
    #         'LastUpdate': LastUpdate,
    #         'Partner_ID': Partner_id,
    #     }
    #     self.env.cr.execute(sql, params)
    #     orderObj = self.env['sale.order']
    #     itemList = []
    #
    #     for val in self.env.cr.dictfetchall():
    #         order_id = val['id']
    #         order = orderObj.browse(order_id)
    #         orderStatus = self._get_current_status(order)
    #
    #         data = [
    #
    #             ('active', '=', True),
    #             # ('parent_id', '=', partner_id.parent_id.id),
    #             ('name', '=', order.name),
    #             ('ship_date', '=', order.expected_date),
    #             ('in_hands', '=', order.in_hands),
    #             ('status', '=', orderStatus),
    #             ('SONumber', '=', order.name)
    #         ]
    #         itemList.append(data)
    #     json_string = json.dumps(itemList)
    #     return itemList
    #
    # def _get_current_status(self, order):
    #     if order.state == 'cancel':
    #         return 'Canceled'
    #     if order.invoice_status == 'invoiced':
    #         return 'Completed'
    #     if order.order_holds:
    #         credit_found = False
    #         has_hold = False
    #         for hold in order.order_holds:
    #             if hold.credit_hold:
    #                 credit_found = True
    #                 return 'Credit Hold'
    #             has_hold = True
    #         if has_hold:
    #             return 'General Hold'
    #     return 'Confirmed'


