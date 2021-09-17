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


class ProductTemplateAttributeValueInherited(models.Model):
    _inherit = 'product.template.attribute.value'

    @api.multi
    def _get_pms_color_code(self):
        for record in self:
            if record.attribute_id:
                attribute_value_id = self.env['product.attribute.value'].search([
                    ('attribute_id', '=', record.attribute_id.id), ('name', 'ilike', record.name),
                    ('html_color', 'ilike', record.html_color)], limit=1)
                if attribute_value_id:
                    record.pms_color = attribute_value_id and attribute_value_id.pms_color and attribute_value_id.pms_color.id

    pms_color = fields.Many2one('product.pms.color', string='PMS Color Code', compute='_get_pms_color_code')
