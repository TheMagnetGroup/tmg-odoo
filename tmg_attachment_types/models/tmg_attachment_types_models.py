# -*- coding: utf-8 -*-

from odoo import models, fields, api


class tmg_attachment_types(models.Model):
    _name = "attachment.type"
    _description = "attachment types"

    name = fields.Char(string="Name")
    description = fields.Char(string="Description")


class tmg_attachment(models.Model):
    _inherit = 'ir.attachment'

    attachment_category = fields.Many2many('attachment.type', help="Attachment Category Tags", required=False)


class tmg_so_attachment(models.Model):
    _inherit = 'sale.order'

    attachments = fields.Many2many('ir.attachment', help="Attachments", required=False)
