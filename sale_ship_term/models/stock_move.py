# Copyright 2021 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).

from odoo import models

class StockMove(models.Model):
    _inherit = 'stock.move'

    def _get_new_picking_values(self):
        res = super(StockMove, self)._get_new_picking_values()
        res.update({
                'shipping_term': self.group_id.sale_id.shipping_term,
                'carrier_account': self.group_id.sale_id.carrier_account,
                'third_party_billing_id':self.group_id.sale_id.third_party_billing_id and self.group_id.sale_id.third_party_billing_id.id,
                'cod_amount':self.group_id.sale_id.amount_total
            })
        return res
