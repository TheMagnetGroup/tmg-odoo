# -*- coding: utf-8 -*-

from odoo import api, fields, models


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    printer_id = fields.Many2one('iot.device', help="Select the printer to which you directly print labels.")