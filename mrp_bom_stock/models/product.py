# -*- coding: utf-8 -*-

from odoo import fields, models, api


class Product(models.Model):
    _inherit = 'product.product'

    def _compute_quantities_dict(self, lot_id, owner_id, package_id, from_date=False, to_date=False):
        res = super(Product, self)._compute_quantities_dict(lot_id, owner_id, package_id, from_date, to_date)
        for product in self.filtered(lambda p: p.bom_id):
            if product.bom_count:
                products = {}
                for line in product.bom_id.bom_line_ids.filtered(lambda l: not l.to_exclude and l.product_id.type != 'consu'):
                    # Calculate product quantity based on uom
                    qty = line.product_qty
                    product_uom_type = line.product_uom_id.uom_type
                    product_uom_factor = line.product_uom_id.factor_inv
                    if product_uom_type == 'bigger':
                        qty = line.product_qty * product_uom_factor
                    elif product_uom_type == 'smaller':
                        qty = line.product_qty / product_uom_factor

                    if line.product_id.id in products.keys():
                        products[line.product_id.id]['qty'] += qty
                    else:
                        products.update({line.product_id.id: {
                            'qty_available': line.product_id.qty_available,
                            'virtual_available': line.product_id.virtual_available,
                            'incoming_qty': line.product_id.incoming_qty,
                            'outgoing_qty': line.product_id.outgoing_qty,
                            'qty': qty}})
                for qty_field in ['qty_available', 'virtual_available', 'incoming_qty', 'outgoing_qty']:
                    possible_qty = []
                    for p in products:
                        possible_qty.append(int(products[p][qty_field] / products[p]['qty']))
                    if possible_qty:
                        res[product.id][qty_field] = min(possible_qty)
        return res

    def action_view_stock_move_lines(self):
        self.ensure_one()
        action = self.env.ref('stock.stock_move_line_action').read()[0]
        action['domain'] = [('product_id', '=', self.id)]
        product_ids = [self.id]
        bom = self.env['mrp.bom'].search(['|', ('product_id', '=', self.id), ('product_tmpl_id', '=', self.product_tmpl_id.id)], limit=1)
        if bom:
            product_ids += bom.bom_line_ids.mapped('product_id').ids
            action['domain'] = [('product_id', 'in', product_ids)]
        return action

    @api.multi
    def action_view_po(self):
        action = self.env.ref('purchase.action_purchase_order_report_all').read()[0]
        action['domain'] = ['&', ('state', 'in', ['purchase', 'done']), ('product_tmpl_id', 'in', self.ids)]
        action['context'] = {
            'search_default_last_year_purchase': 1,
            'search_default_status': 1, 'search_default_order_month': 1,
            'graph_measure': 'unit_quantity'
        }
        bom = self.env['mrp.bom'].search(['|', ('product_id', '=', self.id), ('product_tmpl_id', '=', self.product_tmpl_id.id)], limit=1)
        if bom:
            action = self.env.ref('mrp_bom_stock.action_purchase_line_product_tree').read()[0]
            products = self.product_variant_ids + bom.bom_line_ids.mapped('product_id')
            action['domain'] = [('product_id', 'in', products.ids), ('state', 'in', ['purchase', 'done'])]
        return action

    @api.multi
    def _compute_purchased_product_qty(self):
        """
            override to consider the POL for components as well
        """
        res = super(Product, self)._compute_purchased_product_qty()
        for product in self.filtered(lambda t: t.bom_id):
            product.purchased_product_qty = sum([p.purchased_product_qty for p in (product.bom_id.bom_line_ids.mapped('product_id'))])
        return res

    @api.multi
    def action_open_components_quants(self):
        self.ensure_one()
        products = self + self.bom_id.bom_line_ids.mapped('product_id')
        action = self.env.ref('stock.product_open_quants').read()[0]
        action['domain'] = [('product_id', 'in', products.ids)]
        action['context'] = {
            'search_default_internal_loc': 1,
            'search_default_locationgroup': 1,
            'search_default_productgroup': 1,
        }
        return action

    @api.multi
    def action_open_components_forcasted(self):
        self.ensure_one()
        product_templates = self.product_tmpl_id + self.bom_id.bom_line_ids.mapped('product_id').mapped('product_tmpl_id')
        action = self.env.ref('stock.action_stock_level_forecast_report_template').read()[0]
        action['domain'] = [('product_tmpl_id', 'in', product_templates.ids)]
        action['context'] = {}
        return action


class ProductTemplate(models.Model):
    _inherit = "product.template"

    bom_id = fields.Many2one('mrp.bom', string='Bill of matirial', help="Bill of matirial to compute manufacturable quantities.")

    def action_view_stock_move_lines(self):
        self.ensure_one()
        action = self.env.ref('stock.stock_move_line_action').read()[0]
        action['domain'] = [('product_id.product_tmpl_id', '=', self.id)]
        if self.bom_id:
            product_ids = self.bom_id.bom_line_ids.mapped('product_id').ids
            action['domain'] = [('product_id', 'in', product_ids)]
        return action

    @api.multi
    def action_view_po(self):
        action = self.env.ref('purchase.action_purchase_order_report_all').read()[0]
        action['domain'] = ['&', ('state', 'in', ['purchase', 'done']), ('product_tmpl_id', 'in', self.ids)]
        action['context'] = {
            'search_default_last_year_purchase': 1,
            'search_default_status': 1, 'search_default_order_month': 1,
            'graph_measure': 'unit_quantity'
        }
        if self.bom_id:
            products = self.mapped('product_variant_ids') + self.bom_id.bom_line_ids.mapped('product_id')
            action = self.env.ref('mrp_bom_stock.action_purchase_line_product_tree').read()[0]
            action['domain'] = [('product_id', 'in', products.ids), ('state', 'in', ['purchase', 'done'])]
        return action

    @api.multi
    def _compute_purchased_product_qty(self):
        """
            override to consider the POL for components as well
        """
        res = super(ProductTemplate, self)._compute_purchased_product_qty()
        for template in self.filtered(lambda t: t.bom_id):
            template.purchased_product_qty = sum([p.purchased_product_qty for p in (template.product_variant_ids + template.bom_id.bom_line_ids.mapped('product_id'))])
        return res

    def action_open_quants(self):
        products = self.mapped('product_variant_ids')
        action = self.env.ref('stock.product_open_quants').read()[0]
        action['domain'] = [('product_id', 'in', products.ids)]
        if self.bom_id:
            action = self.env.ref('mrp_bom_stock.action_stock_kit_report_template').read()[0]
            action['domain'] = [('product_tmpl_id', 'in', products.mapped('product_tmpl_id').ids + self.bom_id.bom_line_ids.mapped('product_id').ids)]
        action['context'] = {'search_default_internal_loc': 1}
        return action
