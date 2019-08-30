# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class MrpRouting(models.Model):
    _inherit = "mrp.routing"

    def get_operations(self, attribute_value_ids=False):
        operation_ids = []
        if not attribute_value_ids:
            return [operation for operation in self.operation_ids]
        for operation in self.operation_ids:
            if not operation.attribute_value_ids:
                operation_ids.append(operation)
            for attribute_value in (operation.attribute_value_ids & attribute_value_ids):
                operation_ids.append(operation)
        return operation_ids
