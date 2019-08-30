
from odoo import models, fields, api

class tmg_mo_inhands(models.Model):

    _inherit = "mrp.production"
    in_hands = fields.Datetime(string="In-Hands Date", related="sale_line_order_id.in_hands")