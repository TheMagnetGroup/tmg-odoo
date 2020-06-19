# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class Product(models.Model):
    _inherit = 'product.product'

    def _compute_quantities_dict(self, lot_id, owner_id, package_id, from_date=False, to_date=False):
        """
            Inherited to update quantity fields for manufacturable products
        """
        res = super(Product, self)._compute_quantities_dict(lot_id=lot_id, owner_id=owner_id, package_id=package_id, from_date=from_date, to_date=to_date)
        for product in self.filtered(lambda p: p.bom_id):
            components = product._get_bom_component_qty(product.bom_id)
            res[product.id]['qty_available'] = product._get_possible_assembled_kit(components, res, 'qty_available')
            res[product.id]['incoming_qty'] = product._get_possible_assembled_kit(components, res, 'incoming_qty')
            res[product.id]['outgoing_qty'] = product._get_possible_assembled_kit(components, res, 'outgoing_qty')
            res[product.id]['virtual_available_qty'] = product._get_possible_assembled_kit(components, res, 'virtual_available')
        return res

    @api.multi
    def _get_bom_component_qty(self, bom):
        bom_quantity = self.uom_id._compute_quantity(1.0, bom.product_uom_id)
        boms, lines = bom.explode(self, bom_quantity)
        components = {}
        for line, line_data in lines:
            if not line.to_exclude:
                product = line.product_id.id
                uom = line.product_uom_id
                qty = line.product_qty
                if components.get(product, False):
                    if uom.id != components[product]['uom']:
                        from_uom = uom
                        to_uom = self.env['product.uom'].browse(components[product]['uom'])
                        qty = from_uom._compute_quantity(qty, to_uom)
                    components[product]['qty'] += qty
                else:
                    to_uom = self.browse(product).uom_id
                    if uom.id != to_uom.id:
                        from_uom = uom
                        qty = from_uom._compute_quantity(qty, to_uom)
                    components[product] = {'qty': qty, 'uom': to_uom.id}
        return components

    def _get_possible_assembled_kit(self, components, res_data, field):
        """
            this method will find the possible quantity based on minimum ratio
            TODO: check with jam for possibility of uom conversion ???
        """
        qty_available = []
        for product_id in components:
            product = self.with_context(prefetch_fields=False).browse(product_id)
            qty = res_data.get(product_id, 0) and res_data[product_id][field] or getattr(product, field)
            if not qty:
                qty_available = []
                break
            else:
                qty_available.append(int(qty / components[product_id]['qty']))
        if qty_available:
            return min(qty_available)
        return 0

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
        products = self.env['product.product']
        bom_quantity = self.uom_id._compute_quantity(1.0, self.bom_id.product_uom_id)
        boms, lines = self.bom_id.explode(self, bom_quantity)
        for line, line_data in lines:
            products |= line.product_id
        action = self.env.ref('mrp_bom_stock.product_open_components').read()[0]
        action['domain'] = [('id', 'in', products.ids)]
        return action

    @api.multi
    def action_open_components_forcasted(self):
        self.ensure_one()
        action = self.env.ref('mrp_bom_stock.action_stock_kit_report_pivot').read()[0]
        action['domain'] = [('product_id', '=', self.id)]
        action['context'] = {}
        return action

    def open_incoming_moves_todo(self):
        action_data = self.action_view_stock_move_lines()
        action_data['context'] = {}
        action_data['context'].update({'search_default_todo': 1, 'search_default_done': 0})
        action_data['domain'].append(('move_id.picking_code', '=', 'incoming'))
        return action_data


class ProductTemplate(models.Model):
    _inherit = "product.template"

    bom_id = fields.Many2one('mrp.bom', string='Bill of Material', help="Bill of Material to compute manufacturable quantities.")

    def _compute_quantities_dict(self):
        qty_dict = super(ProductTemplate, self)._compute_quantities_dict()
        for template in self:
            if template.bom_id and any([bol.is_shared() for bol in template.bom_id.bom_line_ids]):
                shared_lines = template.bom_id.bom_line_ids.filtered(lambda bol: bol.is_shared())
                manufacturable_qty = min(shared_lines.mapped('product_id').mapped('qty_available'))
                qty_dict[template.id]['qty_available'] = manufacturable_qty
        return qty_dict

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
            template.purchased_product_qty = sum([p.purchased_product_qty for p in template.product_variant_ids])
        return res

    def action_open_quants(self):
        products = self.mapped('product_variant_ids')
        action = self.env.ref('stock.product_open_quants').read()[0]
        action['context'] = {'search_default_internal_loc': 1}
        if self.bom_id:
            #             products = []
            #             for product in self.mapped('product_variant_ids'):
            #                 bom_quantity = product.uom_id._compute_quantity(1.0, self.bom_id.product_uom_id)
            #                 boms, lines = self.bom_id.explode(product, bom_quantity)
            #                 for line, line_data in lines:
            #                     if line.product_id.id not in products:
            #                         products.append(line.product_id.id)
            #             for line in self.bom_id.bom_line_ids.filtered(lambda l: l.attribute_value_ids and all([av.attribute_id.create_variant == 'never' for av in l.attribute_value_ids])):
            #                 products.append(line.product_id.id)
            action = self.env.ref('mrp_bom_stock.product_open_components').read()[0]
            action['domain'] = [('id', 'in', self.bom_id.bom_line_ids.mapped('product_id').ids)]
            return action
        action['domain'] = [('product_id', 'in', products.ids)]
        return action

    def open_incoming_moves_todo(self):
        action_data = self.action_view_stock_move_lines()
        action_data['context'] = {}
        action_data['context'].update({'search_default_todo': 1, 'search_default_done': 0})
        action_data['domain'].append(('move_id.picking_code', '=', 'incoming'))
        return action_data
