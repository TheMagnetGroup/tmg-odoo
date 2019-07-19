# -*- coding: utf-8 -*-

from odoo import models, fields, api

class tmg_so_inhands(models.Model):

    _inherit = "sale.order"
    in_hands = fields.Date(string="In-Hands Date")
    commitment_date = fields.Datetime('Ship Date',
                                      states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
                                      copy=False, oldname='requested_date', readonly=True,
                                      help="This is the delivery date promised to the customer. If set, the delivery order "
                                           "will be scheduled based on this date rather than product lead times.")
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100