# -*- coding: utf-8 -*-

from odoo import models, fields, api


class tmg_attachment_types(models.Model):
    _inherit = 'ir.attachment'

    attachment_category = fields.Many2many('sale.order', help="Examples include Customer Art, Purchase Order, "
                                                              "Proof, Production Art, etc..")

