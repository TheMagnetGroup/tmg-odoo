from odoo import api, fields, models
from odoo.exceptions import UserError

class DeliveryPackageShipmentsWizard(models.TransientModel):
    _name = 'delivery.package.shipments.wizard'
    _description = 'Delivery Package Wizard'

    picking_id = fields.Many2one('delivery.process.shipments.wizard', ondelete='cascade', string='Picking Wizard')

    packaging_id = fields.Many2one('product.packaging', ondelete='restrict', string='Package Type')
    shipping_weight = fields.Float('Shipping Weight')
    num_packages = fields.Integer('# Packages', default=1)

class DeliveryProcessShipments(models.TransientModel):
    _name = 'delivery.process.shipments.wizard'
    _description = "Delivery Process Shipments"

    # @api.model
    # def default_get(self, fields):
    #     result = super(DeliveryProcessShipments, self).default_get(fields)
    #     result['res_model'] = self._context.get('active_model')
    #     result['res_id'] = self._context.get('active_id')
    #     packaging_id = fields.Many2one('product.packaging', ondelete='restrict', string='Package Type')
    #     shipping_weight = fields.Float('Shipping Weight')
    #     # result['share_link'] = self.env[result['res_model']].browse(result['res_id'])._get_share_url(redirect=True)
    #     return result

    def _default_pickings(self):
        return self.env['stock.picking'].browse(self.env.context.get('active_ids'))

    def _default_picking(self):
        id = self.env['stock.picking'].browse(self.env.context.get('active_ids'))
        return id[0]

    def _default_packages(self):
        picking = self._default_picking()
        if picking and picking.package_ids:
            return self.convert_packages_to('delivery.package.shipments.wizard', picking.package_ids)
        return False
    # delivery_id = fields.Many2one('stock.picking', string="Assigned To")
    # share_link = fields.Char(string="Link", compute='_compute_share_link')
    picking_ids = fields.Many2many('stock.picking', string='Picking', ondelete='cascade', required=True, default=_default_pickings)
    delivery_package_ids = fields.One2many('delivery.package.shipments.wizard', 'picking_id', string='Delivery Packages', default=_default_packages)
    package_picking_id = fields.Many2one('stock.picking', string='Picking', required=True,
                                         default=_default_picking)
    package_carrier_type = fields.Selection(related='package_picking_id.carrier_id.delivery_type')


    @api.multi
    def action_assign_tech(self):
        pickings = self.env['stock.picking'].browse(self._context.get('active_ids'))
        pickings.write({'user_id': self.user_id.id})

    @api.multi
    def action_define_packages_wiz(self):

        pickings = self.env['stock.picking'].browse(self._context.get('active_ids'))
        deliveries = []
        deliveries.extend(pick.carrier_id.delivery_type for pick in pickings)
        deliveries = list(set(deliveries))
        if len(deliveries) > 1:
            warning = 1
        for pick in pickings:
            if pick.id:
                pick.alt_package_ids.unlink()
                if self.delivery_package_ids:
                    packages = self.convert_packages_to('stock.quant.package', self.delivery_package_ids, mode='unfold')
                    pick.write({'alt_package_ids': [(6, 0, packages.ids)]})
                    self.process_done(pick)
                    pick.action_print_labels


        return {'type': 'ir.actions.act_window_close'}
    def get_package_fold_key(self, package):
        return package.packaging_id, package.shipping_weight

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

    def process_done(self, pick_ids):
        pick_to_backorder = self.env['stock.picking']
        pick_to_do = self.env['stock.picking']
        for picking in pick_ids:
            # If still in draft => confirm and assign
            if picking.state == 'draft':
                picking.action_confirm()
                if picking.state != 'assigned':
                    picking.action_assign()
                    if picking.state != 'assigned':
                        raise UserError(_("Could not reserve all requested products. Please use the \'Mark as Todo\' button to handle the reservation manually."))
            for move in picking.move_lines.filtered(lambda m: m.state not in ['done', 'cancel']):
                for move_line in move.move_line_ids:
                    move_line.qty_done = move_line.product_uom_qty
            if picking._check_backorder():
                pick_to_backorder |= picking
                continue
            pick_to_do |= picking
        # Process every picking that do not require a backorder, then return a single backorder wizard for every other ones.
        if pick_to_do:
            pick_to_do.action_done()
        if pick_to_backorder:
            return pick_to_backorder.action_generate_backorder_wizard()
        return False