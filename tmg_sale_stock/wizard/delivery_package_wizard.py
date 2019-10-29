# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class DeliveryPackageWizard(models.TransientModel):
    _name = 'delivery.package.wizard'
    _description = 'Delivery Package Wizard'

    picking_id = fields.Many2one('picking.delivery.package.wizard', ondelete='cascade', string='Picking Wizard')
    
    packaging_id = fields.Many2one('product.packaging', ondelete='restrict', string='Package Type')
    shipping_weight = fields.Float('Shipping Weight')
    num_packages = fields.Integer('# Packages', default=1)
    # tracking_number = fields.Char('Tracking #')

    
class PickingDeliveryPackageWizard(models.TransientModel):
    _name = 'picking.delivery.package.wizard'
    _description = 'Picking Delivery Package Wizard'

    # explicitly pass in context
    def _default_picking(self):
        return self.env['stock.picking'].browse(self.env.context.get('active_id'))

    picking_id = fields.Many2one('stock.picking', string='Picking', ondelete='cascade', required=True, default=_default_picking)

    def _default_packages(self):
        picking = self._default_picking()
        if picking and picking.package_ids:
            return self.convert_packages_to('delivery.package.wizard', picking.package_ids)
        return False

    delivery_package_ids = fields.One2many('delivery.package.wizard', 'picking_id', string='Delivery Packages', default=_default_packages)

    def get_package_fold_key(self, package):
        return package.packaging_id, package.shipping_weight
    
    # a helper function that helps fold regular packages to wizard packages or unfold wizard packages to regular
    # mode can be 'fold' or 'unfold'
    def convert_packages_to(self, dest_model, packages, mode='fold'):
        num_package_mapping = {}
        if mode == 'fold':
            fold_packages = []
            for package in packages:
                key = self.get_package_fold_key(package) 
                if key not in num_package_mapping:
                    fold_packages.append(package)
                num_package_mapping[key] = num_package_mapping.get(key, 0) + 1
            packages = fold_packages
                
        r_packages = self.env[dest_model]
        for package in packages:
            values = {
                'packaging_id': package.packaging_id.id if package.packaging_id else False,
                'shipping_weight': package.shipping_weight,
            }
            
            if mode == 'fold':
                key = self.get_package_fold_key(package)
                values.update({'num_packages': num_package_mapping.get(key, 0)})
                r_packages |= self.env[dest_model].create(values)
            elif mode == 'unfold':
                for i in range(package.num_packages):
                    r_packages |= self.env[dest_model].create(values)

        return r_packages    
    
    def action_define_packages(self):
        self.ensure_one()
        if self.picking_id and self.delivery_package_ids:
            # translate delivery package wizard to regular packages
            packages = self.convert_packages_to('stock.quant.package', self.delivery_package_ids, mode='unfold')
            self.picking_id.alt_package_ids.unlink()  # remove these trash from db
            self.picking_id.write({'alt_package_ids': [(6, 0, packages.ids)]})

        return {'type': 'ir.actions.act_window_close'}
