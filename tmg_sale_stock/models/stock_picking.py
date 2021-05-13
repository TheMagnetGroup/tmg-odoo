# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'
    backorder_channel_id = fields.Many2one('mail.channel', 'Backorder Channel')

class StockQuantPackage(models.Model):
    _inherit = 'stock.quant.package'
    alt_picking_id = fields.Many2one('stock.picking', ondelete='cascade', string='Alt Picking')

    height = fields.Integer(related='packaging_id.height')
    width = fields.Integer(related='packaging_id.width')
    length = fields.Integer(related='packaging_id.length')
    
class StockPicking(models.Model):
    _inherit = 'stock.picking'

    alt_package_ids = fields.One2many('stock.quant.package', 'alt_picking_id', string='Alternative Packages')

    @api.multi
    def button_validate(self):
        self.ensure_one()
        if self.picking_type_code == 'outgoing' and self.carrier_id and not self.package_ids:
            raise ValidationError(_('Please define one or more packages before validating the delivery order.'))
        ''
        if self.picking_type_code == 'internal':
            if not any(found.product_id == ml.product_id for ml in self.move_line_ids_without_package for found in ml.location_id.quant_ids):
                raise ValidationError(_('Invalid location for pick.'))

        return super(StockPicking, self).button_validate()

    @api.one
    @api.depends('move_line_ids', 'move_line_ids.result_package_id', 'alt_package_ids')
    def _compute_packages(self):
        self.ensure_one()
        if self.alt_package_ids:
            self.package_ids = self.alt_package_ids.ids
        else:
            super(StockPicking, self)._compute_packages()

    @api.one
    @api.depends('move_line_ids', 'move_line_ids.result_package_id', 'move_line_ids.product_uom_id', 'move_line_ids.qty_done', 'alt_package_ids')
    def _compute_bulk_weight(self):
        self.ensure_one()
        if self.alt_package_ids:
           self.weight_bulk = 0.0
        else:
            super(StockPicking, self)._compute_bulk_weight()
