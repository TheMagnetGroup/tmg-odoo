    # -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, models, fields, _, tools
from .ups_request import UPS_Request
from odoo.addons.delivery_ups.models.ups_request import Package
from odoo.exceptions import UserError
from odoo.tools import pdf




class ProviderUPS(models.Model):
    _inherit = 'delivery.carrier'

    def _get_ups_service_types(self):
        return [
            ('03', 'UPS Ground'),
            ('11', 'UPS Standard'),
            ('01', 'UPS Next Day'),
            ('14', 'UPS Next Day AM'),
            ('13', 'UPS Next Day Air Saver'),
            ('02', 'UPS 2nd Day'),
            ('59', 'UPS 2nd Day AM'),
            ('12', 'UPS 3-day Select'),
            ('65', 'UPS Saver'),
            ('07', 'UPS Worldwide Express'),
            ('08', 'UPS Worldwide Expedited'),
            ('54', 'UPS Worldwide Express Plus'),
            ('96', 'UPS Worldwide Express Freight')
        ]

    def ups_rate_shipment(self, order):
        superself = self.sudo()
        srm = UPS_Request(self.log_xml, superself.ups_username, superself.ups_passwd, superself.ups_shipper_number, superself.ups_access_number, self.prod_environment)
        ResCurrency = self.env['res.currency']
        max_weight = self.ups_default_packaging_id.max_weight
        packages = []
        total_qty = 0
        total_weight = 0
        for line in order.order_line.filtered(lambda line: not line.is_delivery):
            product_package_ids = line.product_id.packaging_ids
            total_qty += line.product_uom_qty
            total_weight += line.product_id.weight * line.product_qty

            if product_package_ids:
                container_qty = product_package_ids[0].qty or 1
            elif max_weight and total_weight > max_weight:
                total_package = int(total_weight / max_weight)
                last_package_weight = total_weight % max_weight

                for seq in range(total_package):
                    packages.append(Package(self, max_weight))
                if last_package_weight:
                    packages.append(Package(self, last_package_weight))
                continue
            else:
                packages.append(Package(self, total_weight))
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
                packages.append(Package(self, weight,quant_pack=product_package_ids[0]))
            if partial_weight:
                number_of_pack += 1
                packages.append(Package(self, partial_weight, quant_pack= product_package_ids[0]))

        shipment_info = {
            'total_qty': total_qty  # required when service type = 'UPS Worldwide Express Freight'
        }

        if self.ups_cod:
            cod_info = {
                'currency': order.partner_id.country_id.currency_id.name,
                'monetary_value': order.amount_total,
                'funds_code': self.ups_cod_funds_code,
            }
        else:
            cod_info = None

        check_value = srm.check_required_value(order.company_id.partner_id, order.warehouse_id.partner_id, order.partner_shipping_id, order=order)
        if check_value:
            return {'success': False,
                    'price': 0.0,
                    'error_message': check_value,
                    'warning_message': False}
        ups_service_type = order.ups_service_type or self.ups_default_service_type
        result = srm.get_shipping_price(
            shipment_info=shipment_info, packages=packages, shipper=order.company_id.partner_id, ship_from=order.warehouse_id.partner_id,
            ship_to=order.partner_shipping_id, packaging_type=self.ups_default_packaging_id.shipper_package_code, service_type=ups_service_type,
            saturday_delivery=self.ups_saturday_delivery, cod_info=cod_info)

        if result.get('error_message'):
            return {'success': False,
                    'price': 0.0,
                    'error_message': _('Error:\n%s') % result['error_message'],
                    'warning_message': False}

        if order.currency_id.name == result['currency_code']:
            price = float(result['price'])
            list_price = float(result['list_price']) if result.get('list_price') else 0.0
        else:
            quote_currency = ResCurrency.search([('name', '=', result['currency_code'])], limit=1)
            price = quote_currency._convert(
                float(result['price']), order.currency_id, order.company_id, order.date_order or fields.Date.today())
            if result.get('list_price'):
                list_price = quote_currency._convert(float(result['list_price']), order.currency_id, order.company_id,
                                                     order.date_order or fields.Date.today())
            else:
                list_price = 0.0

        if self.ups_bill_my_account and order.ups_carrier_account:
            # Don't show delivery amount, if ups bill my account option is true
            price = 0.0

        return {'success': True,
                'price': price,
                'list_price': list_price,
                'transit': result['transit'],
                'error_message': False,
                'warning_message': False}

    def ups_send_shipping(self, pickings):
        res = []
        superself = self.sudo()
        srm = UPS_Request(self.log_xml, superself.ups_username, superself.ups_passwd, superself.ups_shipper_number, superself.ups_access_number, self.prod_environment)
        ResCurrency = self.env['res.currency']
        for picking in pickings:
            packages = []
            package_names = []
            if picking.package_ids:
                # Create all packages
                for package in picking.package_ids:
                    packages.append(Package(self, package.shipping_weight, quant_pack=package.packaging_id, name=package.name))
                    package_names.append(package.name)
            # Create one package with the rest (the content that is not in a package)
            if picking.weight_bulk:
                packages.append(Package(self, picking.weight_bulk))

            invoice_line_total = 0
            for move in picking.move_lines:
                invoice_line_total += picking.company_id.currency_id.round(move.product_id.lst_price * move.product_qty)

            shipment_info = {
                'description': picking.origin,
                'total_qty': sum(sml.qty_done for sml in picking.move_line_ids),
                'ilt_monetary_value': '%d' % invoice_line_total,
                'itl_currency_code': self.env.user.company_id.currency_id.name,
                'phone': picking.partner_id.mobile or picking.partner_id.phone or picking.sale_id.partner_id.mobile or picking.sale_id.partner_id.phone,

            }
            if picking.sale_id and picking.sale_id.carrier_id != picking.carrier_id:
                ups_service_type = picking.ups_service_type or picking.carrier_id.ups_default_service_type or self.ups_default_service_type
            else:
                ups_service_type = picking.ups_service_type or self.ups_default_service_type
            ups_carrier_account = picking.ups_carrier_account

            if picking.carrier_id.ups_cod:
                cod_info = {
                    'currency': picking.partner_id.country_id.currency_id.name,
                    'monetary_value': picking.sale_id.amount_total,
                    'funds_code': self.ups_cod_funds_code,
                }
            else:
                cod_info = None

            check_value = srm.check_required_value(picking.company_id.partner_id, picking.picking_type_id.warehouse_id.partner_id, picking.partner_id, picking=picking)
            if check_value:
                raise UserError(check_value)

            package_type = picking.package_ids and picking.package_ids[0].packaging_id.shipper_package_code or self.ups_default_packaging_id.shipper_package_code
            pick_one = picking.shipping_reference_2 or picking.sale_id.client_order_ref
            result = srm.send_shipping(
                shipment_info=shipment_info, packages=packages, shipper=picking.company_id.partner_id, ship_from=picking.picking_type_id.warehouse_id.partner_id,
                ship_to=picking.partner_id, packaging_type=package_type, service_type=ups_service_type, label_file_type=self.ups_label_file_type, ups_carrier_account=ups_carrier_account,
                saturday_delivery=picking.carrier_id.ups_saturday_delivery, cod_info=cod_info, shipping_reference_1= picking.sale_id.name, shipping_reference_2=pick_one, company=picking.company_id)
            if result.get('error_message'):
                raise UserError(result['error_message'])

            order = picking.sale_id
            company = order.company_id or picking.company_id or self.env.user.company_id
            currency_order = picking.sale_id.currency_id
            if not currency_order:
                currency_order = picking.company_id.currency_id

            if currency_order.name == result['currency_code']:
                price = float(result['price'])
            else:
                quote_currency = ResCurrency.search([('name', '=', result['currency_code'])], limit=1)
                price = quote_currency._convert(
                    float(result['price']), currency_order, company, order.date_order or fields.Date.today())

            package_labels = []
            for track_number, label_binary_data in result.get('label_binary_data').items():
                package_labels = package_labels + [(track_number, label_binary_data)]

            carrier_tracking_ref = "+".join([pl[0] for pl in package_labels])
            logmessage = _("Shipment created into UPS<br/>"
                           "<b>Tracking Numbers:</b> %s<br/>"
                           "<b>Packages:</b> %s") % (carrier_tracking_ref, ','.join(package_names))
            if self.ups_label_file_type != 'GIF':
                attachments = [('LabelUPS-%s.%s' % (pl[0], self.ups_label_file_type), pl[1]) for pl in package_labels]
            if self.ups_label_file_type == 'GIF':
                attachments = [('LabelUPS.pdf', pdf.merge_pdf([pl[1] for pl in package_labels]))]
            picking.message_post(body=logmessage, attachments=attachments)
            shipping_data = {
                'exact_price': price,
                'tracking_number': carrier_tracking_ref}
            res = res + [shipping_data]
        return res