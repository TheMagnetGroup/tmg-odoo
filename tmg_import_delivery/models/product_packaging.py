# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class ProductPackaging(models.Model):
    _inherit = 'product.packaging'

    max_box_allowed = fields.Integer("Maximum Boxes Per Pallet")
