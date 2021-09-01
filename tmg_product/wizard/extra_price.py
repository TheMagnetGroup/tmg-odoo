# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ConfigureProductAttribute(models.TransientModel):
    _name = "configure.product.attribute"

    parent_id = fields.Many2one('product.pricelist.inquiry.wizard', string="Parent")
    attribute_id = fields.Many2one('product.attribute', string="Attribute")
    value_id = fields.Many2one('product.attribute.value', string="Value")

    @api.onchange('value_id', 'attribute_id')
    def _onchange_value_id(self):
        valid_attributes = self.parent_id.product_id.valid_product_attribute_ids
        valid_attribute_vals = self.parent_id.product_id.valid_product_attribute_value_ids

        return {'domain': {'attribute_id': [('id', 'in', valid_attributes.ids)], 'value_id': [
            ('id', 'in', valid_attribute_vals.ids), ('attribute_id', '=', self.attribute_id.id)]}}

