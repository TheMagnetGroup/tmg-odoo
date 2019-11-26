# -*- coding: utf-8 -*-

from odoo import models, fields, api


class tmg_attachment_types(models.Model):
    _inherit = 'sale.order'
    _description = "attachment types"
    _name = "attachment.type"


name = fields.Char(string="Name")
description = fields.Char(string="Description")


class whatever(models.Model):
    _inherit = 'ir.attachment'

    attachment_category = fields.Many2many('attachment.type', help="Attachment Category Tags", required=False)