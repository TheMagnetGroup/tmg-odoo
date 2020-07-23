# -*- coding: utf-8 -*-

from odoo import models, fields, api


class tmg_attachment_types(models.Model):
    _name = "attachment.type"
    _description = "Attachment Types"

    name = fields.Char(string="Name")
    description = fields.Char(string="Description")

class tmg_sales_attachments(models.Model):
    _inherit = "sale.order"

    attachment_ids = fields.One2many('ir.attachment', compute='_compute_attachment_ids', inverse='_inverse_category_tags', string="Main Attachments")

    def _compute_attachment_ids(self):
        for order in self:
            attachment_ids = self.env['ir.attachment'].search([('res_id', '=', order.id), ('res_model', '=', 'sale.order')]).ids
            message_attachment_ids = order.mapped('message_ids.attachment_ids').ids  # from mail_thread
            order.attachment_ids = list(set(attachment_ids) - set(message_attachment_ids))

    def _inverse_category_tags(self):
        attachment = self.env['ir.attachment'].sudo()
        attachment.write({'attachment_category':[attachment.attachment_category]})


class ProductTemplate(models.Model):
    _inherit = "product.template"

    attachment_ids = fields.One2many('ir.attachment', compute='_compute_attachment_ids', inverse='_inverse_category_tags', string="Main Attachments")

    def _compute_attachment_ids(self):
        for product in self:
            attachment_ids = self.env['ir.attachment'].search([('res_id', '=', product.id), ('res_model', '=', 'product.template')]).ids
            message_attachment_ids = product.mapped('message_ids.attachment_ids').ids  # from mail_thread
            product.attachment_ids = list(set(attachment_ids) - set(message_attachment_ids))

    def _inverse_category_tags(self):
        attachment = self.env['ir.attachment'].sudo()
        attachment.write({'attachment_category':[attachment.attachment_category]})


class tmg_attachment(models.Model):
    _inherit = 'ir.attachment'

    attachment_category = fields.Many2many('attachment.type', help="Attachment Category")
