# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def _action_confirm(self):
        res = super(SaleOrder, self)._action_confirm()
        MrpJobSudo = self.env['mrp.job'].sudo()
        MrpProduction = self.env['mrp.production'].sudo()
        mfg_orders = MrpProduction.search([('origin', 'ilike', self.name), ('job_id', '=', False), ('art_ref', '!=', '')])
        if mfg_orders:
            mfg_tuples = [(m.product_tmpl_id.id, m.art_ref) for m in mfg_orders]
            # remove duplicates
            mfg_tuples = list(set(mfg_tuples))
            mfg_order_prod_dict = dict.fromkeys(mfg_tuples, False)
            for mfg_order in mfg_orders:
                if not mfg_order_prod_dict[(mfg_order.product_tmpl_id.id, mfg_order.art_ref)]:
                    mfg_order_prod_dict[(mfg_order.product_tmpl_id.id, mfg_order.art_ref)] = []
                mfg_order_prod_dict[(mfg_order.product_tmpl_id.id, mfg_order.art_ref)].append(mfg_order.id)
            for prod_art_tpl, mfg_ids in mfg_order_prod_dict.items():
                mrp_job = MrpJobSudo.create({
                    'product_tmpl_id': prod_art_tpl[0],
                    'sale_order_id': self.id,
                    'art_ref': prod_art_tpl[1],
                    'mfg_order_ids': [(6, 0, mfg_ids)]
                    })
                mfg_orders.filtered(lambda m: m.id in mfg_ids).write({'job_id': mrp_job.id})
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
