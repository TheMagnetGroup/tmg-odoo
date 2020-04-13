# -*- coding: utf-8 -*-

from odoo import models, fields, api


# Buying group model
class BuyingGroup(models.Model):
    _name = 'partner.buying.group'
    _description = 'Buying Groups'
    _order = 'name'

    name = fields.Char(string='Buying Group', required=True)
    active = fields.Boolean(default=True, help="The active field allows you to hide the category without removing it.")


class tmg_customer(models.Model):

    _inherit = 'res.partner'

    Rebate = fields.Boolean()
