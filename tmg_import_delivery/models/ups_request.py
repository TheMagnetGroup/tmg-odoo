from odoo.addons.delivery_ups.models.ups_request import UPSRequest, Package

import suds
from suds.client import Client
from suds.plugin import MessagePlugin
from suds.sax.element import Element

SUDS_VERSION = suds.__version__

class UPS_Request(UPSRequest):

    def set_package_detail(self, client, packages, packaging_type, namespace, ship_from, ship_to, cod_info, ref_1, ref_2):
        Packages = []
        for i, p in enumerate(packages):
            package = client.factory.create('{}:PackageType'.format(namespace))
            if hasattr(package, 'Packaging'):
                package.Packaging.Code = p.packaging_type or packaging_type or ''
            elif hasattr(package, 'PackagingType'):
                package.PackagingType.Code = p.packaging_type or packaging_type or ''

            if p.dimension_unit and any(p.dimension.values()):
                package.Dimensions.UnitOfMeasurement.Code = p.dimension_unit or ''
                package.Dimensions.Length = p.dimension['length'] or ''
                package.Dimensions.Width = p.dimension['width'] or ''
                package.Dimensions.Height = p.dimension['height'] or ''

            if cod_info:
                package.PackageServiceOptions.COD.CODFundsCode = str(cod_info['funds_code'])
                package.PackageServiceOptions.COD.CODAmount.MonetaryValue = cod_info['monetary_value']
                package.PackageServiceOptions.COD.CODAmount.CurrencyCode = cod_info['currency']

            package.PackageWeight.UnitOfMeasurement.Code = p.weight_unit or ''
            package.PackageWeight.Weight = p.weight or ''

            # Package and shipment reference text is only allowed for shipments within
            # the USA and within Puerto Rico. This is a UPS limitation.


            ref_count = 0
            if ref_1:
                ref_count += 1
                reference_1 = client.factory.create('ns3:ReferenceNumberType')
                reference_1.Code = "TN"
                reference_1.Value = ref_1
                package.ReferenceNumber.append(reference_1)
            if ref_2:
                ref_count += 1
                reference_2 = client.factory.create('ns3:ReferenceNumberType')
                reference_2.Code = "TN"
                reference_2.Value = ref_2
                package.ReferenceNumber.append(reference_2)

            if ref_count <= 1:
                if (p.name and ship_from.country_id.code in ('US') and ship_to.country_id.code in ('US')):
                    reference_number = client.factory.create('ns3:ReferenceNumberType')
                    reference_number.Code = 'PM'
                    reference_number.Value = p.name
                    reference_number.BarCodeIndicator = p.name
                    package.ReferenceNumber.append(reference_number)

            Packages.append(package)
        return Packages

    def send_shipping(self, shipment_info, packages, shipper, ship_from, ship_to, packaging_type, service_type,
                      saturday_delivery, cod_info=None, label_file_type='GIF', ups_carrier_account=False, shipping_reference_1='', shipping_reference_2='', company = None):
        client = self._set_client(self.ship_wsdl, 'Ship', 'ShipmentRequest')

        request = client.factory.create('ns0:RequestType')
        request.RequestOption = 'nonvalidate'

        namespace = 'ns3'
        label = client.factory.create('{}:LabelSpecificationType'.format(namespace))

        label.LabelImageFormat.Code = label_file_type
        label.LabelImageFormat.Description = label_file_type
        if label_file_type != 'GIF':
            label.LabelStockSize.Height = '6'
            label.LabelStockSize.Width = '4'

        shipment = client.factory.create('{}:ShipmentType'.format(namespace))
        shipment.Description = shipment_info.get('description')

        for package in self.set_package_detail(client, packages, packaging_type, namespace, ship_from, ship_to,
                                               cod_info, shipping_reference_1, shipping_reference_2):
            shipment.Package.append(package)


        shipment.Shipper.AttentionName = shipper.attention_to or ''
        shipment.Shipper.Name = company.shipping_name or ''

        shipment.Shipper.Address.AddressLine = [l for l in [shipper.street or '', shipper.street2 or ''] if l]
        shipment.Shipper.Address.City = shipper.city or ''
        shipment.Shipper.Address.PostalCode = shipper.zip or ''
        shipment.Shipper.Address.CountryCode = shipper.country_id.code or ''
        if shipper.country_id.code in ('US', 'CA', 'IE'):
            shipment.Shipper.Address.StateProvinceCode = shipper.state_id.code or ''
        shipment.Shipper.ShipperNumber = self.shipper_number or ''
        shipment.Shipper.Phone.Number = '2025550195'

        shipment.ShipFrom.AttentionName =  ''
        shipment.ShipFrom.Name = company.shipping_name or ''


        shipment.ShipFrom.Address.AddressLine = [l for l in [ship_from.street or '', ship_from.street2 or ''] if l]
        shipment.ShipFrom.Address.City = ship_from.city or ''
        shipment.ShipFrom.Address.PostalCode = ship_from.zip or ''
        shipment.ShipFrom.Address.CountryCode = ship_from.country_id.code or ''
        if ship_from.country_id.code in ('US', 'CA', 'IE'):
            shipment.ShipFrom.Address.StateProvinceCode = ship_from.state_id.code or ''
        shipment.ShipFrom.Phone.Number = '2025550195'


        shipment.ShipTo.AttentionName = ship_to.attention_to or ''
        shipment.ShipTo.Name = ship_to.parent_id.name or ship_to.name or ''
        shipment.ShipTo.Address.AddressLine = [l for l in [ship_to.street or '', ship_to.street2 or ''] if l]
        shipment.ShipTo.Address.City = ship_to.city or ''
        shipment.ShipTo.Address.PostalCode = ship_to.zip or ''
        shipment.ShipTo.Address.CountryCode = ship_to.country_id.code or ''
        if ship_to.country_id.code in ('US', 'CA', 'IE'):
            shipment.ShipTo.Address.StateProvinceCode = ship_to.state_id.code or ''
        shipment.ShipTo.Phone.Number = self._clean_phone_number(shipment_info['phone'])
        if not ship_to.commercial_partner_id.is_company:
            shipment.ShipTo.Address.ResidentialAddressIndicator = suds.null()

        shipment.Service.Code = service_type or ''
        shipment.Service.Description = 'Service Code'
        if service_type == "96":
            shipment.NumOfPiecesInShipment = int(shipment_info.get('total_qty'))
        shipment.ShipmentRatingOptions.NegotiatedRatesIndicator = 1

        # Shipments from US to CA or PR require extra info
        if ship_from.country_id.code == 'US' and ship_to.country_id.code in ['CA', 'PR']:
            shipment.InvoiceLineTotal.CurrencyCode = shipment_info.get('itl_currency_code')
            shipment.InvoiceLineTotal.MonetaryValue = shipment_info.get('ilt_monetary_value')

        # set the default method for payment using shipper account
        payment_info = client.factory.create('ns3:PaymentInformation')
        shipcharge = client.factory.create('ns3:ShipmentCharge')
        shipcharge.Type = '01'
        # Bill Recevier 'Bill My Account'
        if ups_carrier_account:
            shipcharge.BillReceiver.AccountNumber = ups_carrier_account
            shipcharge.BillReceiver.Address.PostalCode = ship_to.zip
        else:
            shipcharge.BillShipper.AccountNumber = self.shipper_number or ''

        payment_info.ShipmentCharge = shipcharge
        shipment.PaymentInformation = payment_info

        if saturday_delivery:
            shipment.ShipmentServiceOptions.SaturdayDeliveryIndicator = saturday_delivery
        else:
            shipment.ShipmentServiceOptions = ''

        try:
            response = client.service.ProcessShipment(
                Request=request, Shipment=shipment,
                LabelSpecification=label)

            # Check if shipment is not success then return reason for that
            if response.Response.ResponseStatus.Code != "1":
                return self.get_error_message(response.Response.ResponseStatus.Code,
                                              response.Response.ResponseStatus.Description)

            result = {}
            result['label_binary_data'] = {}
            for package in response.ShipmentResults.PackageResults:
                result['label_binary_data'][package.TrackingNumber] = self.save_label(
                    package.ShippingLabel.GraphicImage, label_file_type=label_file_type)
            result['tracking_ref'] = response.ShipmentResults.ShipmentIdentificationNumber
            result['currency_code'] = response.ShipmentResults.ShipmentCharges.TotalCharges.CurrencyCode

            # Some users are qualified to receive negotiated rates
            negotiated_rate = 'NegotiatedRateCharges' in response.ShipmentResults and response.ShipmentResults.NegotiatedRateCharges.TotalCharge.MonetaryValue or None

            result['price'] = negotiated_rate or response.ShipmentResults.ShipmentCharges.TotalCharges.MonetaryValue
            return result

        except suds.WebFault as e:
            # childAtPath behaviour is changing at version 0.6
            prefix = ''
            if SUDS_VERSION >= "0.6":
                prefix = '/Envelope/Body/Fault'
            return self.get_error_message(
                e.document.childAtPath(prefix + '/detail/Errors/ErrorDetail/PrimaryErrorCode/Code').getText(),
                e.document.childAtPath(prefix + '/detail/Errors/ErrorDetail/PrimaryErrorCode/Description').getText())
        except IOError as e:
            return self.get_error_message('0', 'UPS Server Not Found:\n%s' % e)