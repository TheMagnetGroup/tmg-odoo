from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class DeliveryOrder(models.Model):
    _inherit = 'sale.order.line.delivery'
    def _get_ups_service_types(self):
        return self.env['delivery.carrier']._get_ups_service_types()

    def get_fedex_service_types(self):
        return self.env['delivery.carrier'].get_fedex_service_types()


    carrier_id = fields.Many2one('delivery.carrier', string="Delivery Carrier")
    ups_carrier_account = fields.Char(string='Carrier Account', readonly=False)
    ups_service_type = fields.Selection(_get_ups_service_types, string="UPS Service Type")
    fedex_carrier_account = fields.Char(string='Fedex Carrier Account', readonly=False)
    fedex_service_type = fields.Selection(get_fedex_service_types, string="Fedex Service Type")
    scheduled_date = fields.Date(string="Scheduled Date")
    partner_name = fields.Char(related="shipping_partner_id.name")
    street = fields.Char(related="shipping_partner_id.street")
    street2 = fields.Char(related="shipping_partner_id.street2")
    city = fields.Char(related="shipping_partner_id.city")
    state_id = fields.Many2one(related="shipping_partner_id.state_id")
    country_id = fields.Many2one(related="shipping_partner_id.country_id", string="Country")
    attention_to = fields.Char(related='shipping_partner_id.attention_to', string='Attention To')