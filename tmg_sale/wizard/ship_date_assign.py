from odoo import api, fields, models


class ShipDateAssign(models.TransientModel):
    _name = 'portal.ship.assign'
    _description = "Ship Date Assign"

    def _default_so(self):
        return self.env['sale.order'].browse(self.env.context.get('active_ids'))[0]

    sale_id = fields.Many2one('sale.order', string='Active SOs', ondelete='cascade')
    scheduled_date = fields.Datetime(string='New Ship Date')
    access_warning = fields.Text("Access warning", compute="_compute_access_warning")

    @api.multi
    def action_assign_date(self):
        self.ensure_one()
        self.sale_id = self._default_so()
        if self.sale_id:
            self.sale_id.write({'commitment_date': self.scheduled_date})
            manOrds = self.sale_id.production_ids
            dels = self.sale_id.picking_ids


                # d.write({'scheduled_date':  self.scheduled_date})
                # d.scheduled_date = self.scheduled_date
            for m in manOrds:
                # m.write({'date_planned_start':  self.scheduled_date})
                m.date_planned_start = self.scheduled_date
                for p in m.picking.ids:
                    p.write({'scheduled_date': self.scheduled_date})
            for d in dels:
                d.scheduled_date = self.scheduled_date
        return {'type': 'ir.actions.act_window_close'}


