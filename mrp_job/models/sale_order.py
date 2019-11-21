# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, RedirectWarning, \
    ValidationError, Warning

class SaleOrder(models.Model):
    _inherit = "sale.order"

    jobs_count = fields.Integer(compute="_compute_jobs_count", sting="Jobs")

    @api.multi
    @api.depends('order_line', 'order_line.job_id')
    def _compute_jobs_count(self):
        for order in self:
            order.jobs_count = order.order_line and len(order.order_line.mapped('job_id')) or 0

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
            mfg_order_prod_id_mapping = {order.id: order.product_id.id for order in mfg_orders}
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
                mfg_group_orders = mfg_orders.browse(mfg_ids)
                mfg_group_orders.write({'job_id': mrp_job.id})
                if mfg_group_orders.mapped('picking_ids'):
                    mfg_group_orders.mapped('picking_ids').write({'job_id': mrp_job.id})

                for mfg_id in mfg_ids:
                    self.order_line.filtered(lambda l: l.product_id.id == mfg_order_prod_id_mapping[mfg_id]).write({'job_id': mrp_job.id})
        return res

    @api.multi
    def action_view_jobs(self):
        self.ensure_one()
        job_action_data = self.env.ref('mrp_job.action_open_all_jobs').read()[0]
        if self.order_line and self.order_line.mapped('job_id'):
            job_action_data['domain'] = [('id', 'in', self.order_line.mapped('job_id').ids)]
        return job_action_data


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    art_ref = fields.Char(string="Art Reference", required=True, default="to follow...")  # the default permits create() with required art_ref AND reminder to replace later with real entry value
    job_id = fields.Many2one('mrp.job', string="Job Reference", help="Job reference in which MO for this sale order line is included.", copy=False)

    @api.multi
    def _prepare_procurement_values(self, group_id=False):
        values = super(SaleOrderLine, self)._prepare_procurement_values(group_id)
        values['art_ref'] = self.art_ref or ''
        return values

    # These are kept as potential solutions if more specific control of messaging is required in tree/list view
    # @api.model_create_multi
    # def create(self, vals_list):
    #     for values in vals_list:
    #         if values['display_type'] != 'line_section' and values['display_type'] != 'line_note':
    #             if 'art_ref' in values and not values['art_ref']:
    #                 raise ValidationError('Art Reference is required')
    #     result = super(SaleOrderLine, self).create(vals_list)
    #     return result
    #
    # @api.multi
    # def write(self, values):
    #     for line in self:
    #         if 'art_ref' in values and not values['art_ref']:
    #             raise ValidationError('Art Reference is required')
    #     result = super(SaleOrderLine, self).write(values)
    #     return result
