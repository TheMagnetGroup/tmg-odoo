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
            rates = []
            for carrier in carrier_ids:
                res = carrier.rate_shipment(order)
                print('res', res)
                if res['success']:
                    price = res['price']
                    order.delivery_rating_success = True
                    rates.append((0, 0, {'carrier_id': carrier.id,
                                         'transit': res.get('transit', False),
                                         'price': price,
                                         'without_margin_price': res['without_margin'],
                                         'list_price': res.get('list_price', '')}))
                else:
                    continue
            if not rates:
                raise UserError("Currently this service not available!")
            rate_id = self.env['compare.rates'].create({
                'rate_ids': rates
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


