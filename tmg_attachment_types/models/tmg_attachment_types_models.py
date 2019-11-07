# -*- coding: utf-8 -*-

from odoo import models, fields, api


class tmg_attachment_types(models.Model):

    _inherit = 'sale.order'

    attachment_category = fields.Many2many('ir.attachment', help="Examples include Customer Art, Purchase Order, "
                                                                 "Proof, Production Art, etc..")
