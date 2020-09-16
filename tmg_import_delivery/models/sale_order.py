from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def get_fedex_service_types(self):
        return self.env['delivery.carrier'].get_fedex_service_types()

    # Some type of default for this field for the SO Number
    shipping_reference_1 = fields.Char(string="Shipping Reference 1", copy=False)
    shipping_reference_2 = fields.Char(string="Shipping Reference", copy=False)
    fedex_bill_my_account = fields.Boolean(related='carrier_id.fedex_bill_my_account', readonly=True)
    fedex_service_type = fields.Selection(get_fedex_service_types, string="Fedex Service Type")
    fedex_carrier_account = fields.Char(string='FedEx Carrier Account', copy=False)



