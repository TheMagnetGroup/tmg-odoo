# -*- coding: utf-8 -*-
import base64
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re


class CompareRates(models.TransientModel):
    _name = 'compare.rates'
    _description = 'Compare rates of different delivery carrier enabled'

    rate_ids = fields.One2many('compare.all.rates', 'rate_id', string="Compare Rates")
    package_ids = fields.One2many('compare.package.data', 'rate_id', string="Package Details")


class CompareAllRates(models.TransientModel):
    _name = 'compare.all.rates'
    _description = 'Rate details in compare rates pop up'

    rate_id = fields.Many2one('compare.rates', string="Rate")
    carrier_id = fields.Many2one('delivery.carrier', string="Carrier")
    price = fields.Float(string="Marked Up Price")
    without_margin_price = fields.Float(string="Negotiated Price")
    transit = fields.Char(string="Transit Time")
    list_price = fields.Char(string="List Price")
    package_details = fields.Text(string="Package Details")
    billing_weight = fields.Float(string="Billing Weight")

    def set_delivery_price(self):
        order_id = self.env['sale.order'].browse(self._context.get('active_id'))
        order_id.carrier_id = self.carrier_id.id
        order_id.delivery_price = self.price
        order_id.set_delivery_line()


class ComparePackageData(models.TransientModel):
    _name = 'compare.package.data'
    _description = 'Package details in compare rate pop up'

    rate_id = fields.Many2one('compare.rates', string="Rate")
    carrier_name = fields.Char(string="Carrier")
    product_id = fields.Many2one('product.product', string="Product")
    package_dimension = fields.Char(string="Dimension")
    calculated_weight = fields.Float(string="Calculated Weight")
    pieces_per_box = fields.Integer(string="Number of pieces per box")
