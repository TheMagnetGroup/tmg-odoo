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
    def set_shipper(self, company_partner, warehouse_partner):
        Contact = self.client.factory.create('Contact')
        Contact.PersonName = company_partner.attention_to or ''
        Contact.CompanyName = company_partner.name if company_partner.is_company else ''
        Contact.PhoneNumber = warehouse_partner.phone or ''
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