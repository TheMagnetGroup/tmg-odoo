# -*- coding: utf-8 -*-

from odoo import models, fields, api


# Buying group model
class BuyingGroup(models.Model):
    _inherit = 'crm.lead'

    category = fields.Selection([
        ('hqstock', 'High Quantity Stock Items'),
        ('cqstock', 'Catalog Quantity Stock'),
        ('outsourced', 'Outsource')
    ], string='Category', required=True)
    in_hands = fields.Date(string='In Hands Date', help="The estimated in hands date from the customer.")


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    quote_total = fields.Boolean(string="Show Totals On Quote", default=False)