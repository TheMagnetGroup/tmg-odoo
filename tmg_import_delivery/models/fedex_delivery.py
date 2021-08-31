import logging
import time

from odoo import api, models, fields, _, tools
from odoo.exceptions import UserError
from odoo.tools import pdf

from .fedex_request import Fedex_Request
_logger = logging.getLogger(__name__)

FEDEX_CURR_MATCH = {
    u'UYU': u'UYP',
    u'XCD': u'ECD',
    u'MXN': u'NMP',
    u'KYD': u'CID',
    u'CHF': u'SFR',
    u'GBP': u'UKL',
    u'IDR': u'RPA',
    u'DOP': u'RDD',
    u'JPY': u'JYE',
    u'KRW': u'WON',
    u'SGD': u'SID',
    u'CLP': u'CHP',
    u'JMD': u'JAD',
    u'KWD': u'KUD',
    u'AED': u'DHS',
    u'TWD': u'NTD',
    u'ARS': u'ARN',
    u'LVL': u'EURO',
}
def _convert_curr_iso_fdx(code):
    return FEDEX_CURR_MATCH.get(code, code)


class Delivery_Fedex(models.Model):
    _inherit = 'delivery.carrier'

    use_shopping_rate = fields.Boolean("Use On Shopping Rate", copy=False, default=False)

    def rate_shipment(self, order):
        ''' Compute the price of the order shipment

        :param order: record of sale.order
        :return dict: {'success': boolean,
                       'price': a float,
                       'error_message': a string containing an error message,
                       'warning_message': a string containing a warning message}
                       # TODO maybe the currency code?
        '''
        self.ensure_one()
        if hasattr(self, '%s_rate_shipment' % self.delivery_type):
            res = getattr(self, '%s_rate_shipment' % self.delivery_type)(order)
            res['without_margin'] = res['price']
            res['transit'] = res.get('transit', False)
            # apply margin on computed price
            res['price'] = float(res['price']) * (1.0 + (float(self.margin) / 100.0))
            # free when order is large enough
            if res['success'] and self.free_over and order._compute_amount_total_without_delivery() >= self.amount:
                res['warning_message'] = _('Info:\nThe shipping is free because the order amount exceeds %.2f.\n(The actual shipping cost is: %.2f)') % (self.amount, res['price'])
                res['price'] = 0.0
            return res

    def get_fedex_service_types(self):
        return [('INTERNATIONAL_ECONOMY', 'INTERNATIONAL_ECONOMY'),
                                           ('INTERNATIONAL_PRIORITY', 'INTERNATIONAL_PRIORITY'),
                                           ('FEDEX_GROUND', 'FEDEX_GROUND'),
                                           ('FEDEX_2_DAY', 'FEDEX_2_DAY'),
                                           ('FEDEX_2_DAY_AM', 'FEDEX_2_DAY_AM'),
                                           ('FEDEX_3_DAY_FREIGHT', 'FEDEX_3_DAY_FREIGHT'),
                                           ('FIRST_OVERNIGHT', 'FIRST_OVERNIGHT'),
                                           ('PRIORITY_OVERNIGHT', 'PRIORITY_OVERNIGHT'),
                                           ('STANDARD_OVERNIGHT', 'STANDARD_OVERNIGHT'),
                                           ('FEDEX_NEXT_DAY_EARLY_MORNING', 'FEDEX_NEXT_DAY_EARLY_MORNING'),
                                           ('FEDEX_NEXT_DAY_MID_MORNING', 'FEDEX_NEXT_DAY_MID_MORNING'),
                                           ('FEDEX_NEXT_DAY_AFTERNOON', 'FEDEX_NEXT_DAY_AFTERNOON'),
                                           ('FEDEX_NEXT_DAY_END_OF_DAY', 'FEDEX_NEXT_DAY_END_OF_DAY'),
                                           ('FEDEX_EXPRESS_SAVER', 'FEDEX_EXPRESS_SAVER')]

    fedex_bill_my_account = fields.Boolean(string='Bill My Account',
                                         help="If checked, ecommerce users will be prompted their FedEx account number\n"
                                              "and delivery fees will be charged on it.")
    # fedex_service_type = fields.Selection(get_fedex_service_types, string="UPS Service Type", default='03')
    def _convert_curr_iso_fdx(self, code):
        return FEDEX_CURR_MATCH.get(code, code)

    def _convert_curr_fdx_iso(self,code):
        curr_match = {v: k for k, v in FEDEX_CURR_MATCH.items()}
        return curr_match.get(code, code)

    def fedex_rate_shipment(self, order):
        max_weight = self._fedex_convert_weight(self.fedex_default_packaging_id.max_weight, self.fedex_weight_unit)
        price = 0.0
        is_india = order.partner_shipping_id.country_id.code == 'IN' and order.company_id.partner_id.country_id.code == 'IN'
        order_currency = order.currency_id
        superself = self.sudo()

        # Authentication stuff
        srm = Fedex_Request(self.log_xml, request_type="rating", prod_environment=self.prod_environment)
        srm.web_authentication_detail(superself.fedex_developer_key, superself.fedex_developer_password)
        srm.client_detail(superself.fedex_account_number, superself.fedex_meter_number)

        # Build basic rating request and set addresses
        srm.transaction_detail(order.name)
        srm.shipment_request(
            self.fedex_droppoff_type,
            self.fedex_service_type,
            self.fedex_default_packaging_id.shipper_package_code,
            self.fedex_weight_unit,
            self.fedex_saturday_delivery,
        )
        pkg = self.fedex_default_packaging_id

        srm.set_currency(_convert_curr_iso_fdx(order_currency.name))
        srm.set_shipper(order.company_id, order.warehouse_id.partner_id, order.partner_shipping_id)
        srm.set_recipient(order.partner_shipping_id)
        total_weight = 0
        total_pack = 0
        master_pack_default = False
        package_list = []
        for line in order.order_line.filtered(lambda l: l.product_id.type == 'product'):
            product_package_ids = line.product_id.packaging_ids
            est_weight_value = line.product_id.weight * line.product_uom_qty
            weight_value = self._fedex_convert_weight(est_weight_value, self.fedex_weight_unit)

            if weight_value > 0.0:
                weight_value = max(weight_value, 0.01)
            if product_package_ids:
                container_qty = product_package_ids[0].qty or 1
                package_id = product_package_ids[0]
            elif max_weight and weight_value > max_weight:
                total_package = int(weight_value / max_weight)
                last_package_weight = weight_value % max_weight
                for sequence in range(1, total_package + 1):
                    srm.add_package(
                        max_weight,
                        package_code=pkg.shipper_package_code,
                        package_height=pkg.height,
                        package_width=pkg.width,
                        package_length=pkg.length,
                        sequence_number=sequence,
                        mode='rating',
                    )
                if last_package_weight:
                    total_package = total_package + 1
                    srm.add_package(
                        last_package_weight,
                        package_code=pkg.shipper_package_code,
                        package_height=pkg.height,
                        package_width=pkg.width,
                        package_length=pkg.length,
                        sequence_number=total_package,
                        mode='rating',
                    )
                srm.set_master_package(weight_value, total_package)
                master_pack_default = True
                continue
            else:

                srm.add_package(
                    weight_value,
                    package_code=pkg.shipper_package_code,
                    package_height=pkg.height,
                    package_width=pkg.width,
                    package_length=pkg.length,
                    mode='rating',
                )
                srm.set_master_package(weight_value, 1)
                master_pack_default = True
                continue

            if line.product_uom_qty % container_qty == 0:
                number_of_pack = line.product_uom_qty/container_qty
                partial_qty = 0
            else:
                partial_qty = line.product_uom_qty % container_qty
                number_of_pack = ((line.product_uom_qty - partial_qty)/container_qty)
            weight = line.product_id.weight * container_qty
            partial_weight = line.product_id.weight * partial_qty
            for sequence in range(1, int(number_of_pack) + 1):
                total_weight += weight

                srm.add_package(
                    weight,
                    package_code=pkg.shipper_package_code,
                    package_height=product_package_ids[0].height,
                    package_width=product_package_ids[0].width,
                    package_length=product_package_ids[0].length,
                    sequence_number=sequence,
                    mode='rating',
                )
                package_list.append({'product_id': line.product_id.id,
                                     'package_dimension': '%sx%sx%s' %
                                                          (package_id.length, package_id.width, package_id.height),
                                     'weight': weight,
                                     'number_of_pieces': container_qty})
            if partial_weight:
                total_weight += partial_weight
                number_of_pack += 1
                srm.add_package(
                    partial_weight,
                    package_code=pkg.shipper_package_code,
                    package_height=product_package_ids[0].height,
                    package_width=product_package_ids[0].width,
                    package_length=product_package_ids[0].length,
                    sequence_number=int(number_of_pack) + 1,
                    mode='rating',
                )
                package_list.append({'product_id': line.product_id.id,
                                     'package_dimension': '%sx%sx%s' %
                                                          (package_id.length, package_id.width, package_id.height),
                                     'weight': partial_weight,
                                     'number_of_pieces': partial_qty})
            total_weight = self._fedex_convert_weight(total_weight, self.fedex_weight_unit)
            total_pack += number_of_pack
        if not master_pack_default:
            srm.set_master_package(int(total_weight), int(total_pack))

        # Commodities for customs declaration (international shipping)
        if self.fedex_service_type in ['INTERNATIONAL_ECONOMY', 'INTERNATIONAL_PRIORITY'] or is_india:
            total_commodities_amount = 0.0
            commodity_country_of_manufacture = order.warehouse_id.partner_id.country_id.code

            for line in order.order_line.filtered(lambda l: l.product_id.type in ['product', 'consu']):
                commodity_amount = line.price_reduce_taxinc
                total_commodities_amount += (commodity_amount * line.product_uom_qty)
                commodity_description = line.product_id.name
                commodity_number_of_piece = '1'
                commodity_weight_units = self.fedex_weight_unit
                commodity_weight_value = self._fedex_convert_weight(line.product_id.weight * line.product_uom_qty, self.fedex_weight_unit)
                commodity_quantity = line.product_uom_qty
                commodity_quantity_units = 'EA'
                # DO NOT FORWARD PORT AFTER 12.0
                if getattr(line.product_id, 'hs_code', False):
                    commodity_harmonized_code = line.product_id.hs_code or ''
                else:
                    commodity_harmonized_code = ''
                srm._commodities(_convert_curr_iso_fdx(order_currency.name), commodity_amount, commodity_number_of_piece, commodity_weight_units, commodity_weight_value, commodity_description, commodity_country_of_manufacture, commodity_quantity, commodity_quantity_units, commodity_harmonized_code)
            srm.customs_value(_convert_curr_iso_fdx(order_currency.name), total_commodities_amount, "NON_DOCUMENTS")
            srm.duties_payment(order.warehouse_id.partner_id.country_id.code, superself.fedex_account_number)

        request = srm.rate()

        warnings = request.get('warnings_message')
        if warnings:
            _logger.info(warnings)

        if not request.get('errors_message'):
            price = self._get_request_price(request['price'], order, order_currency)
        else:
            return {'success': False,
                    'price': 0.0,
                    'error_message': _('Error:\n%s') % request['errors_message'],
                    'warning_message': False}

        if self.fedex_bill_my_account and order.fedex_carrier_account:
            # Don't show delivery amount, if ups bill my account option is true
            price = 0.0

        return {'success': True,
                'price': price,
                'error_message': False,
                'transit': request.get('transit_time', ''),
                'list_price': request.get('list_price', ''),
                'warning_message': _('Warning:\n%s') % warnings if warnings else False,
                'billing_weight': request.get('billing_weight', 0),
                'package_list': package_list}

    def fedex_send_shipping(self, pickings):
        res = []

        for picking in pickings:

            srm = Fedex_Request(self.log_xml, request_type="shipping", prod_environment=self.prod_environment)
            superself = self.sudo()
            # if picking.fedex_carrier_account:
            #     fedex_number = picking.fedex_carrier_account
            # else
            #     fedex_number =superself.fedex_carrier
            fedex_number = picking.fedex_carrier_account or superself.fedex_account_number
            srm.web_authentication_detail(superself.fedex_developer_key, superself.fedex_developer_password)
            srm.client_detail(superself.fedex_account_number, superself.fedex_meter_number)

            srm.transaction_detail(picking.id)
            new_fedex_service_type = picking.fedex_service_type or self.fedex_service_type
            package_type = picking.package_ids and picking.package_ids[0].packaging_id.shipper_package_code or self.fedex_default_packaging_id.shipper_package_code
            srm.shipment_request(self.fedex_droppoff_type, new_fedex_service_type, package_type, self.fedex_weight_unit, self.fedex_saturday_delivery)
            srm.set_currency(self._convert_curr_iso_fdx(picking.company_id.currency_id.name))
            srm.set_shipper(picking.company_id, picking.picking_type_id.warehouse_id.partner_id, picking.partner_id)
            srm.set_recipient(picking.partner_id)
            third_party_billing = picking.fedex_carrier_account
            # Here is where the change matters.
            if picking.shipping_reference_2:
                po_number = picking.shipping_reference_2
            else:
                po_number = picking.sale_id.client_order_ref

            dept_number = picking.sale_id.name
            # dept_number = picking.shipping_reference_2
            srm.shipping_charges_payment(fedex_number)
            if third_party_billing:
                srm.RequestedShipment.ShippingChargesPayment.PaymentType = 'THIRD_PARTY'



            srm.shipment_label('COMMON2D', self.fedex_label_file_type, self.fedex_label_stock_type, 'TOP_EDGE_OF_TEXT_FIRST', 'SHIPPING_LABEL_FIRST')

            order = picking.sale_id
            company = order.company_id or picking.company_id or self.env.user.company_id
            order_currency = picking.sale_id.currency_id or picking.company_id.currency_id

            net_weight = self._fedex_convert_weight(picking.shipping_weight, self.fedex_weight_unit)
            net_weight = 1
            # Commodities for customs declaration (international shipping)
            if self.fedex_service_type in ['INTERNATIONAL_ECONOMY', 'INTERNATIONAL_PRIORITY'] or (picking.partner_id.country_id.code == 'IN' and picking.picking_type_id.warehouse_id.partner_id.country_id.code == 'IN'):

                commodity_currency = order_currency
                total_commodities_amount = 0.0
                commodity_country_of_manufacture = picking.picking_type_id.warehouse_id.partner_id.country_id.code

                for operation in picking.move_line_ids:
                    commodity_amount = operation.move_id.sale_line_id.price_unit or operation.product_id.list_price
                    total_commodities_amount += (commodity_amount * operation.qty_done)
                    commodity_description = operation.product_id.name
                    commodity_number_of_piece = '1'
                    commodity_weight_units = self.fedex_weight_unit
                    commodity_weight_value = self._fedex_convert_weight(operation.product_id.weight * operation.qty_done, self.fedex_weight_unit)
                    commodity_quantity = operation.qty_done
                    commodity_quantity_units = 'EA'
                    # DO NOT FORWARD PORT AFTER 12.0
                    if getattr(operation.product_id, 'hs_code', False):
                        commodity_harmonized_code = operation.product_id.hs_code or ''
                    else:
                        commodity_harmonized_code = ''
                    srm._commodities(self._convert_curr_iso_fdx(commodity_currency.name), commodity_amount, commodity_number_of_piece, commodity_weight_units, commodity_weight_value, commodity_description, commodity_country_of_manufacture, commodity_quantity, commodity_quantity_units, commodity_harmonized_code)
                srm.customs_value(self._convert_curr_iso_fdx(commodity_currency.name), total_commodities_amount, "NON_DOCUMENTS")
                srm.duties_payment(picking.picking_type_id.warehouse_id.partner_id.country_id.code, superself.fedex_account_number)

            package_count = len(picking.package_ids) or 1

            # For india picking courier is not accepted without this details in label.
            # po_number = dept_number = False
            if picking.partner_id.country_id.code == 'IN' and picking.picking_type_id.warehouse_id.partner_id.country_id.code == 'IN':
                po_number = 'B2B' if picking.partner_id.commercial_partner_id.is_company else 'B2C'
                dept_number = 'BILL D/T: SENDER'

            # TODO RIM master: factorize the following crap

            ################
            # Multipackage #
            ################
            if package_count > 1:

                # Note: Fedex has a complex multi-piece shipping interface
                # - Each package has to be sent in a separate request
                # - First package is called "master" package and holds shipping-
                #   related information, including addresses, customs...
                # - Last package responses contains shipping price and code
                # - If a problem happens with a package, every previous package
                #   of the shipping has to be cancelled separately
                # (Why doing it in a simple way when the complex way exists??)

                master_tracking_id = False
                package_labels = []
                carrier_tracking_ref = ""

                for sequence, package in enumerate(picking.package_ids, start=1):

                    package_weight = self._fedex_convert_weight(package.shipping_weight, self.fedex_weight_unit)
                    packaging = package.packaging_id
                    srm._add_package(
                        package_weight,
                        package_code=packaging.shipper_package_code,
                        package_height=packaging.height,
                        package_width=packaging.width,
                        package_length=packaging.length,
                        sequence_number=sequence,
                        po_number=po_number,
                        dept_number=dept_number,
                    )
                    srm.set_master_package(net_weight, package_count, master_tracking_id=master_tracking_id)
                    request = srm.process_shipment()
                    package_name = package.name or sequence

                    warnings = request.get('warnings_message')
                    if warnings:
                        _logger.info(warnings)

                    # First package
                    if sequence == 1:
                        if not request.get('errors_message'):
                            master_tracking_id = request['master_tracking_id']
                            package_labels.append((package_name, srm.get_label()))
                            carrier_tracking_ref = request['tracking_number']
                        else:
                            raise UserError(request['errors_message'])

                    # Intermediary packages
                    elif sequence > 1 and sequence < package_count:
                        if not request.get('errors_message'):
                            package_labels.append((package_name, srm.get_label()))
                            carrier_tracking_ref = carrier_tracking_ref + "," + request['tracking_number']
                        else:
                            raise UserError(request['errors_message'])

                    # Last package
                    elif sequence == package_count:
                        # recuperer le label pdf
                        if not request.get('errors_message'):
                            package_labels.append((package_name, srm.get_label()))

                            if self._convert_curr_iso_fdx(order_currency.name) in request['price']:
                                carrier_price = request['price'][self._convert_curr_iso_fdx(order_currency.name)]
                            else:
                                _logger.info("Preferred currency has not been found in FedEx response")
                                company_currency = picking.company_id.currency_id
                                if self._convert_curr_iso_fdx(company_currency.name) in request['price']:
                                    amount = request['price'][self._convert_curr_iso_fdx(company_currency.name)]
                                    carrier_price = company_currency._convert(
                                        amount, order_currency, company, order.date_order or fields.Date.today())
                                else:
                                    amount = request['price']['USD']
                                    carrier_price = company_currency._convert(
                                        amount, order_currency, company, order.date_order or fields.Date.today())

                            carrier_tracking_ref = carrier_tracking_ref + "," + request['tracking_number']

                            logmessage = _("Shipment created into Fedex<br/>"
                                           "<b>Tracking Numbers:</b> %s<br/>"
                                           "<b>Packages:</b> %s") % (carrier_tracking_ref, ','.join([pl[0] for pl in package_labels]))
                            if self.fedex_label_file_type != 'PDF':
                                attachments = [('LabelFedex-%s.%s' % (pl[0], self.fedex_label_file_type), pl[1]) for pl in package_labels]
                            if self.fedex_label_file_type == 'PDF':
                                attachments = [('LabelFedex.pdf', pdf.merge_pdf([pl[1] for pl in package_labels]))]
                            picking.message_post(body=logmessage, attachments=attachments)
                            shipping_data = {'exact_price': carrier_price,
                                             'tracking_number': carrier_tracking_ref}
                            res = res + [shipping_data]
                        else:
                            raise UserError(request['errors_message'])

            # TODO RIM handle if a package is not accepted (others should be deleted)

            ###############
            # One package #
            ###############
            elif package_count == 1:
                packaging = picking.package_ids[:1].packaging_id or picking.carrier_id.fedex_default_packaging_id
                srm._add_package(
                    net_weight,
                    package_code=packaging.shipper_package_code,
                    package_height=packaging.height,
                    package_width=packaging.width,
                    package_length=packaging.length,
                    po_number=po_number,
                    dept_number=dept_number,
                )
                srm.set_master_package(net_weight, 1)

                # Ask the shipping to fedex
                request = srm.process_shipment()

                warnings = request.get('warnings_message')
                if warnings:
                    _logger.info(warnings)

                if not request.get('errors_message'):

                    if self._convert_curr_iso_fdx(order_currency.name) in request['price']:
                        carrier_price = request['price'][self._convert_curr_iso_fdx(order_currency.name)]
                    else:
                        _logger.info("Preferred currency has not been found in FedEx response")
                        company_currency = picking.company_id.currency_id
                        if self._convert_curr_iso_fdx(company_currency.name) in request['price']:
                            amount = request['price'][self._convert_curr_iso_fdx(company_currency.name)]
                            carrier_price = company_currency._convert(
                                amount, order_currency, company, order.date_order or fields.Date.today())
                        else:
                            amount = request['price']['USD']
                            carrier_price = company_currency._convert(
                                amount, order_currency, company, order.date_order or fields.Date.today())

                    carrier_tracking_ref = request['tracking_number']
                    logmessage = (_("Shipment created into Fedex <br/> <b>Tracking Number : </b>%s") % (carrier_tracking_ref))

                    fedex_labels = [('LabelFedex-%s-%s.%s' % (carrier_tracking_ref, index, self.fedex_label_file_type), label)
                                    for index, label in enumerate(srm._get_labels(self.fedex_label_file_type))]
                    picking.message_post(body=logmessage, attachments=fedex_labels)

                    shipping_data = {'exact_price': carrier_price,
                                     'tracking_number': carrier_tracking_ref}
                    res = res + [shipping_data]
                else:
                    raise UserError(request['errors_message'])

            ##############
            # No package #
            ##############
            else:
                raise UserError(_('No packages for this picking'))

        return res

