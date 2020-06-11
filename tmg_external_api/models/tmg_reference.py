# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, datetime
import json


class tmg_reference(models.Model):
    _name = 'tmg_external_api.tmg_reference'
    name = fields.Char(string= "Name")
    category = fields.Char(string="Category")
    value = fields.Char(string="Value")

    def getEnums(self, categoryPassed):
        cont = self.env['tmg_external_api.tmg_reference']
        recs = cont.search([('category', '=', categoryPassed)])
        output = []
        for r in recs:
            t = [r.name, r.value]
            output.append(t)
        return output

