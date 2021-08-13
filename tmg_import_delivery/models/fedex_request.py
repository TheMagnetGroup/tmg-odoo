from odoo.addons.delivery_fedex.models.fedex_request import FedexRequest

STATECODE_REQUIRED_COUNTRIES = ['US', 'CA', 'PR ', 'IN']

class Fedex_Request(FedexRequest):

    def _add_package(self, weight_value, package_code=False, package_height=0, package_width=0, package_length=0, sequence_number=False, mode='shipping', po_number=False, dept_number=False):
        package = self.client.factory.create('RequestedPackageLineItem')
        package_weight = self.client.factory.create('Weight')
        package_weight.Value = weight_value
        package_weight.Units = self.RequestedShipment.TotalWeight.Units

        package.PhysicalPackaging = 'BOX'
        if package_code == 'YOUR_PACKAGING':
            package.Dimensions.Height = package_height
            package.Dimensions.Width = package_width
            package.Dimensions.Length = package_length
            # TODO in master, add unit in product packaging and perform unit conversion
            package.Dimensions.Units = "IN" if self.RequestedShipment.TotalWeight.Units == 'LB' else 'CM'
        if po_number:
            po_reference = self.client.factory.create('CustomerReference')
            po_reference.CustomerReferenceType = 'CUSTOMER_REFERENCE'
            po_reference.Value = po_number
            package.CustomerReferences.append(po_reference)
        if dept_number:
            dept_reference = self.client.factory.create('CustomerReference')
            dept_reference.CustomerReferenceType = 'P_O_NUMBER'
            dept_reference.Value = dept_number
            package.CustomerReferences.append(dept_reference)

        package.Weight = package_weight
        if mode == 'rating':
            package.GroupPackageCount = 1
        if sequence_number:
            package.SequenceNumber = sequence_number
        else:
            self.hasOnePackage = True

        if mode == 'rating':
            self.RequestedShipment.RequestedPackageLineItems.append(package)
        else:
            self.RequestedShipment.RequestedPackageLineItems = package

    def set_recipient(self, recipient_partner):
        Contact = self.client.factory.create('Contact')
        if recipient_partner.is_company:
            Contact.PersonName = recipient_partner.attention_to or ''
            Contact.CompanyName = recipient_partner.name
        else:
            Contact.PersonName = recipient_partner.attention_to or ''
            Contact.CompanyName = recipient_partner.name or ''
        Contact.PhoneNumber = recipient_partner.phone or ''

        Address = self.client.factory.create('Address')
        Address.StreetLines = [recipient_partner.street or '', recipient_partner.street2 or '']
        Address.City = recipient_partner.city or ''
        if recipient_partner.country_id.code in STATECODE_REQUIRED_COUNTRIES:
            Address.StateOrProvinceCode = recipient_partner.state_id.code or ''
        else:
            Address.StateOrProvinceCode = ''
        Address.PostalCode = recipient_partner.zip or ''
        Address.CountryCode = recipient_partner.country_id.code or ''

        self.RequestedShipment.Recipient.Contact = Contact
        self.RequestedShipment.Recipient.Address = Address

    def set_currency(self, currency):
        self.RequestedShipment.PreferredCurrency = currency
        # ask Fedex to include our preferred currency in the response
        self.RequestedShipment.RateRequestTypes = ['PREFERRED', 'LIST']

    def rate(self):
        formatted_response = {'price': {}}
        del self.ClientDetail.Region
        if self.hasCommodities:
            self.RequestedShipment.CustomsClearanceDetail.Commodities = self.listCommodities

        try:
            self.response = self.client.service.getRates(WebAuthenticationDetail=self.WebAuthenticationDetail,
                                                         ClientDetail=self.ClientDetail,
                                                         TransactionDetail=self.TransactionDetail,
                                                         Version=self.VersionId,
                                                         ReturnTransitAndCommit=True,
                                                         RequestedShipment=self.RequestedShipment)


            if (self.response.HighestSeverity != 'ERROR' and self.response.HighestSeverity != 'FAILURE'):
                if not getattr(self.response, "RateReplyDetails", False):
                    raise Exception("No rating found")
                transit_time = self.response.RateReplyDetails[0].TransitTime
                formatted_response['transit_time'] = transit_time and transit_time.replace('_',' ')
                for rating in self.response.RateReplyDetails[0].RatedShipmentDetails:
                    if rating.ShipmentRateDetail.RateType == 'PAYOR_ACCOUNT_PACKAGE':
                        formatted_response['price'][rating.ShipmentRateDetail.TotalNetFedExCharge.Currency] = rating.ShipmentRateDetail.TotalNetFedExCharge.Amount
                    elif rating.ShipmentRateDetail.RateType == 'PAYOR_LIST_PACKAGE':
                        formatted_response['list_price'] = rating.ShipmentRateDetail.TotalNetFedExCharge.Amount

                if len(self.response.RateReplyDetails[0].RatedShipmentDetails) == 1:
                    if 'CurrencyExchangeRate' in self.response.RateReplyDetails[0].RatedShipmentDetails[0].ShipmentRateDetail:
                        formatted_response['price'][self.response.RateReplyDetails[0].RatedShipmentDetails[0].ShipmentRateDetail.CurrencyExchangeRate.FromCurrency] = self.response.RateReplyDetails[0].RatedShipmentDetails[0].ShipmentRateDetail.TotalNetFedExCharge.Amount / self.response.RateReplyDetails[0].RatedShipmentDetails[0].ShipmentRateDetail.CurrencyExchangeRate.Rate
            else:
                errors_message = '\n'.join([("%s: %s" % (n.Code, n.Message)) for n in self.response.Notifications if (n.Severity == 'ERROR' or n.Severity == 'FAILURE')])
                formatted_response['errors_message'] = errors_message

            if any([n.Severity == 'WARNING' for n in self.response.Notifications]):
                warnings_message = '\n'.join([("%s: %s" % (n.Code, n.Message)) for n in self.response.Notifications if n.Severity == 'WARNING'])
                formatted_response['warnings_message'] = warnings_message

        except suds.WebFault as fault:
            formatted_response['errors_message'] = fault
        except IOError:
            formatted_response['errors_message'] = "Fedex Server Not Found"
        except Exception as e:
            formatted_response['errors_message'] = e.args[0]

        return formatted_response


    def set_shipper(self, company_partner, warehouse_partner, actual_partner):
        Contact = self.client.factory.create('Contact')

        Contact.PersonName =  ''
        Contact.CompanyName = company_partner.shipping_name
        Contact.PhoneNumber = '2025550195'


        # TODO fedex documentation asks for TIN number, but it seems to work without

        Address = self.client.factory.create('Address')
        Address.StreetLines = [warehouse_partner.street or '', warehouse_partner.street2 or '']
        Address.City = warehouse_partner.city or ''
        if warehouse_partner.country_id.code in STATECODE_REQUIRED_COUNTRIES:
            Address.StateOrProvinceCode = warehouse_partner.state_id.code or ''
        else:
            Address.StateOrProvinceCode = ''
        Address.PostalCode = warehouse_partner.zip or ''
        Address.CountryCode = warehouse_partner.country_id.code or ''

        self.RequestedShipment.Shipper.Contact = Contact
        self.RequestedShipment.Shipper.Address = Address