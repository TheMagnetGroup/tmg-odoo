# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)

class SaleReport(models.Model):
    _inherit = 'sale.report'

    in_hands = fields.Date('In Hands Date', readonly=True)
    decoration_method = fields.Char('Decoration Method', readonly=True)
    commitment_date = fields.Date('Ship Date', readonly=True)
    on_hold = fields.Boolean('On Hold', readonly=True)
    on_production_hold = fields.Boolean('On Production Hold', readonly=True)
    purchase_price = fields.Float('Cost', readonly=True)
    material = fields.Float('Material', readonly=True)
    labor = fields.Float('Labor', readonly=True)
    overhead = fields.Float('Overhead', readonly=True)

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['in_hands'] = ', s.in_hands as in_hands'
        fields['decoration_method'] = ', l.decoration_method as decoration_method'
        fields['commitment_date'] = ', s.commitment_date'
        fields['on_hold'] = ', s.on_hold'
        fields['on_production_hold'] = ', s.on_production_hold'
        fields['purchase_price'] = ', sum(l.purchase_price)'
        fields['material'] = ', sum(l.material_cost) as material'
        fields['labor'] = ', sum(l.labor_cost) as labor'
        fields['overhead'] = ', sum(l.overhead_cost) as overhead'

        groupby += ', s.in_hands, l.decoration_method, s.commitment_date, s.on_hold, s.on_production_hold'

        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)
