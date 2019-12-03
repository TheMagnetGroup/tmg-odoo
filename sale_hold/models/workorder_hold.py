from odoo import models, fields, api, exceptions
from odoo.exceptions import UserError

class workorder_hold(models.Model):
    _inherit = 'mrp.workorder'
    on_hold = fields.Boolean(string="On Hold")

    @api.multi
    def record_production(self):
        if self.on_hold:
            raise UserError('This order has holds preventing processing.')
        ret = super(workorder_hold, self).record_production()
        return ret

    @api.multi
    def process_order(self):
        if self.on_hold:
            raise UserError('This order has holds preventing processing.')
        ret = super(workorder_hold, self).process_order()
        return ret