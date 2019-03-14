# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    job_id = fields.Many2one('mrp.job', string="Job reference", help="Job reference in which this MO is included")
    art_ref = fields.Char(string="Art Reference")

    @api.multi
    def produce_product(self):
        self.ensure_one()
        if self.workorder_ids:
            action_data = self.env.ref('mrp.action_mrp_workorder_production_specific').read()[0]
            return action_data
        else:
            return self.open_produce_product()


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    @api.multi
    def process_order(self):
        self.ensure_one()
        workorder_view = self.env.ref('mrp.mrp_production_workorder_form_view_inherit')
        return {
            'name': _(self.name),
            'domain': [],
            'res_model': 'mrp.workorder',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'view_id': workorder_view.id,
            'views': [(workorder_view.id, 'form')],
            'view_mode': 'form',
            'view_type': 'form',
        }
