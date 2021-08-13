# -*- coding: utf-8 -*-
import base64
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re


class CompareRates(models.TransientModel):
    _name = 'compare.rates'

    rate_ids = fields.One2many('compare.all.rates', 'rate_id', string="Compare Rates")


class CompareAllRates(models.TransientModel):
    _name = 'compare.all.rates'

    rate_id = fields.Many2one('compare.rates', string="Rate")
    carrier_id = fields.Many2one('delivery.carrier', "Carrier")
    price = fields.Float("Marked Up Price")
    without_margin_price = fields.Float("Negotiated Price")
    transit = fields.Char('Transit Time')
    list_price = fields.Char("List Price")

    def set_delivery_price(self):
        order_id = self.env['sale.order'].browse(self._context.get('active_id'))
        order_id.carrier_id = self.carrier_id.id
        order_id.delivery_price = self.price
        order_id.set_delivery_line()

