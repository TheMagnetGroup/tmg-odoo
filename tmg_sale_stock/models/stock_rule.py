# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, registry, _

import logging
_logger = logging.getLogger(__name__)


class ProcurementGroup(models.Model):

    _inherit = 'procurement.group'

    @api.model
    def run(self, product_id, product_qty, product_uom, location_id, name, origin, values):
        rule = self._get_rule(product_id, location_id, values)
        if values.get('skip_procurement'):
            return True
        return super(ProcurementGroup, self).run(product_id, product_qty, product_uom, location_id, name, origin, values)

