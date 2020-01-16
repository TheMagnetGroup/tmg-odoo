# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # requirement of payment terms for a sales order will be enforced in the sale order form view
    payment_term_id = fields.Many2one(required=False)
