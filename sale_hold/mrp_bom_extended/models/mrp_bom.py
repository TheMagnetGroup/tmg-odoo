# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    def _skip_bom_line(self, product):
        """ Control if a BoM line should be produce, can be inherited for add
        custom control. It currently checks that all variant values are in the
        product. """
        product_attribute_value_ids = product.attribute_value_ids
        if self.env.context.get('inactive_attribute_value_ids'):
            product_attribute_value_ids += self.env.context.get('inactive_attribute_value_ids')
        if self.attribute_value_ids:
            if not product or self.attribute_value_ids - product_attribute_value_ids:
                return True
        return False
