# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def _action_confirm(self):
        res = super(SaleOrder, self)._action_confirm()
        mfg_orders = self.env['mrp.production'].sudo().search([('origin', 'ilike', self.name), ('job_id', '=', False)])
        MrpJobSudo = self.env['mrp.job'].sudo()
        if mfg_orders:
            for mfg_order in mfg_orders:
                mrp_job = MrpJobSudo.create({
                    'product_tmpl_id': mfg_order.product_tmpl_id.id,
                    'sale_order_id': self.id,
                    'mfg_order_ids': [(4, mfg_order.id)],
                    'art_ref': self.order_line.filtered(lambda l: l.product_id == mfg_order.product_id).art_ref
                    })
                mfg_order.job_id = mrp_job.id
        return res


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    art_ref = fields.Char(string="Art Reference")
    job_id = fields.Many2one('mrp.job', string="Job Reference", help="Job reference in which MO for this sale order line is included.")

    @api.multi
    def _prepare_procurement_values(self, group_id=False):
        values = super(SaleOrderLine, self)._prepare_procurement_values(group_id)
        values['art_ref'] = self.art_ref or ''
        return values
