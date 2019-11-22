# -*- coding: utf-8 -*-

from odoo import models, fields, api


class tmg_attachment_types(models.Model):
    _inherit = 'sale.order'

    class attachment_type(models.Model):
        _name = 'attachment.type'

    attachment_category = fields.Many2many('ir.attachment', help="Attachment Category Tags")
