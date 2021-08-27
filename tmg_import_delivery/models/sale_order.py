from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def get_fedex_service_types(self):
        return self.env['delivery.carrier'].get_fedex_service_types()

    # Some type of default for this field for the SO Number
    shipping_reference_1 = fields.Char(string="Shipping Reference 1", copy=False)
    shipping_reference_2 = fields.Char(string="Shipping Reference", copy=False)
    fedex_bill_my_account = fields.Boolean(related='carrier_id.fedex_bill_my_account', readonly=True)
    fedex_service_type = fields.Selection(get_fedex_service_types, string="Fedex Service Type")
    fedex_carrier_account = fields.Char(string='FedEx Carrier Account', copy=False)

    def compare_rates(self):
        '''
        Gives freight rates of all use on shipping rates delivery methods
        '''
        for order in self:
            if not order.order_line:
                raise UserError("Please select the products to ship.")
            carrier_ids = self.env['delivery.carrier'].search([('use_shopping_rate', '=', True)])
            if not carrier_ids:
                raise UserError("No delivery method available for use on shopping rates.")
            if not all([product_id.packaging_ids for product_id in order.order_line.filtered(
                    lambda line: line.product_id.type == 'product').mapped('product_id')]):
                raise UserError("Product Packaging must be set before comparing rates")
            rates = []
            packages = []
            product_list = []
            for carrier in carrier_ids:
                res = carrier.with_context(compare_rate=True).rate_shipment(order)
                transit_ups_dict = res.get('transit_days_dict', {})
                if res['success']:
                    price = res['price']
                    if transit_ups_dict:
                        transit_ups = transit_ups_dict.get(carrier.name, False)
                        transit_ups += " DAYS" if transit_ups else transit_ups
                    order.delivery_rating_success = True
                    rates.append((0, 0, {'carrier_id': carrier.id,
                                         'transit': res.get('transit', False) or transit_ups,
                                         'price': price,
                                         'without_margin_price': res['without_margin'],
                                         'list_price': res.get('list_price', '')}))
                    if res.get('package_list') and res.get('package_list')[0].get('product_id', False) not in product_list:
                        for package in res.get('package_list'):
                            packages.append((0, 0, {
                                # 'carrier_name': carrier.name,
                                'product_id': package.get('product_id', False),
                                'package_dimension': package.get('package_dimension', ''),
                                'calculated_weight': package.get('weight', 0),
                                'pieces_per_box': package.get('number_of_pieces', 0)}))
                        product_list.append(res.get('package_list')[0].get('product_id', False))
                else:
                    continue
            if not rates:
                raise UserError("Currently this service not available")
            rate_id = self.env['compare.rates'].create({
                'rate_ids': rates, 'package_ids': packages
            })
            form_view = self.env.ref('tmg_import_delivery.compare_rate_view').id
            return {
                'name': _('Compare Rates'),
                'res_model': 'compare.rates',
                'res_id': rate_id.id,
                'views': [(form_view, 'form'),],
                'type': 'ir.actions.act_window',
                'target': 'new'
            }


