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
    scheduled_date = fields.Date(string="Scheduled Date")
