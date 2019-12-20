# -*- coding: utf-8 -*-

from odoo import api, fields, models


class IotDevice(models.Model):
    _inherit = 'iot.device'

    warehouse_id = fields.Many2one("stock.warehouse", help="Warehouse under which this printer is available.")
