# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    inactive_attribute_value_ids = fields.Many2many(
        'product.attribute.value', string='Inactive Variant Attributes',
        help="Product Variants used on configurator that set no create and will be used in selection of the raw materials.")

    def _prepare_procurement_values(self):
        result = super(StockMove, self)._prepare_procurement_values()
        result.update({'inactive_attribute_value_ids': [(4, avi.id) for avi in self.inactive_attribute_value_ids]})
        return result
    
    def action_explode(self):
        """ Explodes pickings """
        """ Complete re-writing of method because context on skip bom line was not passed. """
        # in order to explode a move, we must have a picking_type_id on that move because otherwise the move
        # won't be assigned to a picking and it would be weird to explode a move into several if they aren't
        # all grouped in the same picking.
        if not self.picking_type_id:
            return self
        bom = self.env['mrp.bom'].sudo()._bom_find(product=self.product_id, company_id=self.company_id.id)
        if not bom or bom.type != 'phantom':
            return self
        phantom_moves = self.env['stock.move']
        processed_moves = self.env['stock.move']
        factor = self.product_uom._compute_quantity(self.product_uom_qty, bom.product_uom_id) / bom.product_qty
        # Custom Code(Passing inactive_attribute_value_ids in context when exploding bom)
        boms, lines = bom.with_context({'inactive_attribute_value_ids': self.inactive_attribute_value_ids}).sudo().explode(self.product_id, factor, picking_type=bom.picking_type_id)
        # Custom code ends
        for bom_line, line_data in lines:
            phantom_moves += self._generate_move_phantom(bom_line, line_data['qty'])
        for new_move in phantom_moves:
            processed_moves |= new_move.action_explode()
#         if not self.split_from and self.procurement_id:
#             # Check if procurements have been made to wait for
#             moves = self.procurement_id.move_ids
#             if len(moves) == 1:
#                 self.procurement_id.write({'state': 'done'})
        if processed_moves and self.state == 'assigned':
            # Set the state of resulting moves according to 'assigned' as the original move is assigned
            processed_moves.write({'state': 'assigned'})
        # delete the move with original product which is not relevant anymore
        self.sudo().unlink()
        return processed_moves
