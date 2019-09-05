from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class StockMove(models.Model):
    _inherit = 'stock.move'
    def _get_ups_service_types(self):
        return self.env['delivery.carrier']._get_ups_service_types()
    
    ups_carrier_account = fields.Char(related='sale_id.ups_carrier_account', string='Carrier Account', readonly=False)
    ups_service_type = fields.Selection(_get_ups_service_types, string="UPS Service Type")