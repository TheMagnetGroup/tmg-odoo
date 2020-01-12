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


    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['in_hands'] = ', s.in_hands as in_hands'
        fields['decoration_method'] = ', l.decoration_method as decoration_method'
        fields['commitment_date'] = ', s.commitment_date'

        groupby += ', s.in_hands, l.decoration_method, s.commitment_date'

        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)
