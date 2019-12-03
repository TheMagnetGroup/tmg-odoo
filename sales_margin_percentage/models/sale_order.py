# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2018-Today Ascetic Business Solution <www.asceticbs.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################

from odoo import api, models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    margin_percentage = fields.Char(compute='_get_average_margin_percentage', string='Margin Percentage')

    @api.one
    @api.depends('order_line','order_line.product_uom_qty','order_line.price_unit', 'order_line.discount', 'order_line.purchase_price')
    def _get_average_margin_percentage(self):
        sale_price = discount = cost = margin_amount = 0.0
        line_cost = line_margin_amount = margin_percentage = 0.0
        for record in self:
            if record.order_line:
                for line in record.order_line:
                    sale_price = line.price_unit * line.product_uom_qty
                    discount = (sale_price * line.discount)/100
                    cost = line.purchase_price * line.product_uom_qty
                    line_cost += cost
                    margin_amount = (sale_price - discount) - cost
                    line_margin_amount += margin_amount
                if line_cost:
                    margin_percentage = (line_margin_amount / line_cost) * 100
                else:
                    margin_percentage = 100
                record.margin_percentage = str(round(margin_percentage,2)) + ' %'

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    margin_percentage = fields.Char(compute='_get_total_percentage', string='Margin Percentage')

    @api.one
    @api.depends('product_uom_qty','price_unit', 'discount', 'purchase_price')
    def _get_total_percentage(self):
        sale_price = discount = cost = margin_amount = margin_percentage = 0.0
        for record in self:
            if record.product_id:
                sale_price = record.price_unit * record.product_uom_qty
                discount = (sale_price*record.discount)/100
                cost = record.purchase_price * record.product_uom_qty
                margin_amount = (sale_price - discount) - cost
                if cost:
                    margin_percentage = (margin_amount / cost) * 100 
                else:
                    margin_percentage = 100 
                record.margin_percentage = str(round(margin_percentage,2)) + ' %'
