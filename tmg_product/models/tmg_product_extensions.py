# -*- coding: utf-8 -*-

from odoo import models, fields, api

class tmg_product_template_tags(models.Model):
    _name = 'product.template.tags'
    _description = "Product Tags"

    name = fields.Char(string='Name',required=True)
    color = fields.Integer(string='Color Index')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists!"),
    ]