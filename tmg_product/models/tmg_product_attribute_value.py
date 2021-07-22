# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProductAttributeValueInherited(models.Model):
    _inherit = 'product.attribute.value'

    pms_color = fields.Many2one('product.pms.color', string='PMS Color Code', help='Enter the PMS Color code only, eg: 110')


class ProductPmsColor(models.Model):
    _name = 'product.pms.color'
    _description = 'PMS Color Codes'

    name = fields.Char(string='PMS Color')
