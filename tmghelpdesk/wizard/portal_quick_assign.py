from odoo import api, fields, models


class PortalQuickAssign(models.TransientModel):
    _name = 'portal.quick.assign'
    _description = "Portal Quick Assign"

    @api.model
    def default_get(self, fields):
        result = super(PortalQuickAssign, self).default_get(fields)
        result['res_model'] = self._context.get('active_model')
        result['res_id'] = self._context.get('active_id')
        # result['share_link'] = self.env[result['res_model']].browse(result['res_id'])._get_share_url(redirect=True)
        return result

    res_model = fields.Char('Related Document Model', required=True)
    res_id = fields.Integer('Related Document ID', required=True)
    user_id = fields.Many2one('res.users', string="Assigned To")
    # share_link = fields.Char(string="Link", compute='_compute_share_link')
    access_warning = fields.Text("Access warning", compute="_compute_access_warning")

    @api.multi
    def action_assign_tech(self):
        tickets = self.env['helpdesk.ticket'].browse(self._context.get('active_ids'))
        tickets.write({'user_id': self.user_id.id})

    @api.depends('res_model', 'res_id')
    def _compute_access_warning(self):
        for rec in self:
            res_model = self.env[rec.res_model]
            if isinstance(res_model, self.pool['portal.mixin']):
                record = res_model.browse(rec.res_id)
                rec.access_warning = record.access_warning
