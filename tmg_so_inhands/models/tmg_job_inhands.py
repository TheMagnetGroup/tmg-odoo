
from odoo import models, fields, api

class tmg_job_inhands(models.Model):

    _inherit = "mrp.job"
    in_hands = fields.Datetime(string="In-Hands Date", related="sale_order_id.in_hands")