# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class MrpJob(models.Model):
    """
    Manufacturing JOB:
    ==================
    Multiple manufacturing order processing from a single object.
    Widely used in printing industry.
    """
    _name = "mrp.job"
    _description = "Manufacturing JOB"

    name = fields.Char(string='Job Reference', required=True, copy=False, readonly=True, index=True)
    product_tmpl_id = fields.Many2one('product.template', string="Product", help="Product to be manufactured.")
    sale_order_id = fields.Many2one('sale.order', string="Sale Order", help="Sale order from where this Job has created.")
    mfg_order_ids = fields.Many2many('mrp.production', 'mrp_job_mrp_prod_rel', 'job_id', 'prod_order_id', string="Manufacturing Orders", help="Associated manufacturing orders.")
    workorder_ids = fields.Many2many('mrp.workorder', string="Workorders", compute="_compute_workorder_ids", help="Workorders associated with the associated manufacturing orders.")
    date_planned_start = fields.Datetime(string='Deadline', compute="_compute_date_planned_start")
    art_ref = fields.Char(string="Art Reference")
    so_notes = fields.Text(related='sale_order_id.note', string="Notes")
    status = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], compute="_compute_job_state", default="draft")
    qty = fields.Float(string="Quantity To Produce", digits=dp.get_precision('Product Unit of Measure'), compute="_compute_qty_to_produce", help="Total quantity to produce combining all manufacturing orders.")
    picking_count = fields.Integer(compute="_compute_picking_count")

    @api.multi
    @api.depends('mfg_order_ids', 'mfg_order_ids.state')
    def _compute_job_state(self):
        for record in self:
            if all([mo.state == 'done' for mo in record.mfg_order_ids]):
                record.status = 'done'
            elif all([mo.state in ['confirmed', 'planned'] for mo in record.mfg_order_ids]) or all([mo.state in ['confirmed', 'planned', 'cancel'] for mo in record.mfg_order_ids]):
                record.status = 'confirm'
            elif any([mo.state == 'progress' for mo in record.mfg_order_ids]) or any([mo.state in ['draft', 'done'] for mo in record.mfg_order_ids]):
                record.status = 'in_progress'
            elif all([mo.state == 'cancel' for mo in record.mfg_order_ids]):
                record.status = 'cancel'
            else:
                record.status = 'draft'

    @api.multi
    @api.depends('mfg_order_ids', 'mfg_order_ids.product_qty')
    def _compute_qty_to_produce(self):
        for record in self:
            record.qty = sum(record.mfg_order_ids and record.mfg_order_ids.mapped('product_qty') or [])

    @api.multi
    def _compute_picking_count(self):
        for record in self:
            record.picking_count = len(record.mfg_order_ids and record.mfg_order_ids.mapped('picking_ids' or []))

    @api.multi
    @api.depends('mfg_order_ids')
    def _compute_workorder_ids(self):
        for record in self:
            record.workorder_ids = record.mfg_order_ids and record.mfg_order_ids.mapped('workorder_ids') or []

    @api.model
    def create(self, vals):
        vals['name'] = "New"
        if vals.get('art_ref', False) and vals.get('sale_order_id', False) and vals.get('product_tmpl_id', False):
            sale_order = self.env['sale.order'].browse(vals.get('sale_order_id'))
            product_tmpl_id = self.env['product.template'].browse(vals.get('product_tmpl_id'))
            job_name = '-'.join([vals.get('art_ref'), sale_order.name, product_tmpl_id.name])
            vals['name'] = job_name
        return super(MrpJob, self).create(vals)

    @api.multi
    def go_to_mrp_job_pickings(self):
        self.ensure_one()
        picking_action = self.env.ref("stock.action_picking_tree_all").read()[0]
        picking_action['domain'] = [('id', 'in', self.mfg_order_ids and self.mfg_order_ids.mapped('picking_ids').ids or [])]
        return picking_action

    @api.multi
    @api.depends('mfg_order_ids', 'mfg_order_ids.date_planned_start')
    def _compute_date_planned_start(self):
        for record in self:
            if record.mfg_order_ids:
                record.date_planned_start = min(record.mfg_order_ids.mapped('date_planned_start'))

    @api.multi
    def action_mark_as_done(self):
        self.ensure_one()
        for mo in self.mfg_order_ids:
            mo.button_mark_done()
