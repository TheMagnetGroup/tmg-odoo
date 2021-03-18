# -*- coding: utf-8 -*-
from odoo import models, fields, api, _



class Warehouse(models.Model):
    _inherit = 'stock.warehouse'

    backorder_channel_id = fields.Many2one('mail.channel', 'Backorder Channel')