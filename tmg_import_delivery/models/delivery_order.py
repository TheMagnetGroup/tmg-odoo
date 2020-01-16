from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class DeliveryOrder(models.Model):
    _inherit = 'sale.order.line.delivery'
    def _get_ups_service_types(self):
        return self.env['delivery.carrier']._get_ups_service_types()


    carrier_id = fields.Many2one('delivery.carrier', string="Delivery Carrier")
    ups_carrier_account = fields.Char(string='Carrier Account', readonly=False)
    ups_service_type = fields.Selection(_get_ups_service_types, string="UPS Service Type")
    fedex_carrier_account = fields.Char(string='Fedex Carrier Account', readonly=False)
    fedex_service_type = fields.Selection([('INTERNATIONAL_ECONOMY', 'INTERNATIONAL_ECONOMY'),
                                           ('INTERNATIONAL_PRIORITY', 'INTERNATIONAL_PRIORITY'),
                                           ('FEDEX_GROUND', 'FEDEX_GROUND'),
                                           ('FEDEX_2_DAY', 'FEDEX_2_DAY'),
                                           ('FEDEX_2_DAY_AM', 'FEDEX_2_DAY_AM'),
                                           ('FEDEX_3_DAY_FREIGHT', 'FEDEX_3_DAY_FREIGHT'),
                                           ('FIRST_OVERNIGHT', 'FIRST_OVERNIGHT'),
                                           ('PRIORITY_OVERNIGHT', 'PRIORITY_OVERNIGHT'),
                                           ('STANDARD_OVERNIGHT', 'STANDARD_OVERNIGHT')], string="Fedex Service Type")
    scheduled_date = fields.Date(string="Scheduled Date")
    partner_name = fields.Char(related="shipping_partner_id.name")
    street = fields.Char(related="shipping_partner_id.street")
    street2 = fields.Char(related="shipping_partner_id.street2")
    city = fields.Char(related="shipping_partner_id.city")
    state_id = fields.Many2one(related="shipping_partner_id.state_id")
    country_id = fields.Many2one(related="shipping_partner_id.country_id", string="Country")