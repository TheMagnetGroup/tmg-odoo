# -*- coding: utf-8 -*-

from odoo import fields, models


class Product(models.Model):
    _inherit = 'product.product'

    def _compute_quantities_dict(self, lot_id, owner_id, package_id, from_date=False, to_date=False):
        res = super(Product, self)._compute_quantities_dict(lot_id, owner_id, package_id, from_date, to_date)
        MrpBom = self.env['mrp.bom']
        for product in self:
            if product.bom_count:
                products = {}
                domain = [('product_tmpl_id', '=', product.product_tmpl_id.id)]
                if product.product_variant_count > 1:
                    domain = [('product_id', '=', product.id)]
                for line in MrpBom.search(domain, limit=1).bom_line_ids.filtered(lambda l: not l.to_exclude and l.product_id.type != 'consu'):
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
        bom = self.env['mrp.bom'].search([('product_tmpl_id', '=', self.product_tmpl_id.id)], limit=1)
        if bom:
            product_ids += bom.bom_line_ids.mapped('product_id').ids
            action['domain'] = [('product_id', 'in', product_ids)]
        return action


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def action_view_stock_move_lines(self):
        self.ensure_one()
        action = self.env.ref('stock.stock_move_line_action').read()[0]
        action['domain'] = [('product_id.product_tmpl_id', '=', self.id)]
        product_ids = [self.id]
        bom = self.env['mrp.bom'].search([('product_tmpl_id', '=', self.id)], limit=1)
        if bom:
            product_ids += bom.bom_line_ids.mapped('product_id').ids
            action['domain'] = [('product_id', 'in', product_ids)]
        return action
