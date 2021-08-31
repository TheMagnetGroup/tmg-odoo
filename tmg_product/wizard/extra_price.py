# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ConfigureProductAttribute(models.TransientModel):
    _name = "configure.product.attribute"

    parent_id = fields.Many2one('product.pricelist.inquiry.wizard', "Parent")
    attribute_id = fields.Many2one('product.attribute', "Attribute")
    value_id = fields.Many2one('product.attribute.value', "Value")
    extra_price = fields.Float("Extra Price")


    @api.onchange('value_id', 'attribute_id')
    def _onchange_value_id(self):
        for rec in self:
            value_id = self.env['product.template.attribute.value'].search([('product_tmpl_id', '=', rec.parent_id.product_id.id),
                                                                             ('name', '=', rec.value_id.name)], limit=1)
            rec.extra_price = value_id.price_extra
        valid_attributes = rec.parent_id.product_id.valid_product_attribute_ids
        valid_attribute_vals = rec.parent_id.product_id.valid_product_attribute_value_ids

        return {'domain': {'attribute_id': [('id', 'in', valid_attributes.ids)], 'value_id': [('id', 'in', valid_attribute_vals.ids), ('attribute_id', '=', rec.attribute_id.id)]}}

