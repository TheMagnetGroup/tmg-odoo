from odoo import models, fields, api
from odoo.exceptions import UserError

class picking_sales_hold(models.Model):
    _inherit = "stock.picking"
    quick_ship = fields.Boolean("Quick Ship", copy=False)
