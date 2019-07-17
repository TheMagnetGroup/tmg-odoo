
from odoo import models, fields, api

class tmg_do_inhands(models.Model):

    _inherit = "stock.picking"
    in_hands = fields.Date(string="In-Hands Date", related="sale_id.in_hands")