# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class tmg_product_pricelist_grid_wizard(models.TransientModel):
    _name = "product.pricelist.inquiry.grid.wizard"
    _description = "Product Pricelist Grid Inquiry"

    product_id = fields.Many2one("product.pricelist.inquiry.wizard", string="Product", ondelete="cascade")
    product_variant_name = fields.Char(string="Product Variant")
    catalog_pricelist = fields.Char(string="Catalog Pricelist")
    net_pricelist = fields.Char(string="Net Pricelist")
    quantity = fields.Float(string="Quantity")
    catalog_price = fields.Float(string="Catalog Price")
    net_price = fields.Float(string="Net Price")
    discount_code = fields.Char(sring="Discount Code")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    published = fields.Boolean(string="Published")
    extra_price = fields.Float(string="Extra Price")


class tmg_product_pricelist_wizard(models.TransientModel):
    _name = 'product.pricelist.inquiry.wizard'
    _description = "Product Pricelist Inquiry"

    # explicitly pass in context
    def _default_product(self):
        p = self.env['product.template'].browse(self.env.context.get('active_id'))
        return p

    product_id = fields.Many2one('product.template', string='Product', ondelete='cascade', required=True, default=_default_product)
    extra_price = fields.Float("Extra Price")
    configure_variants = fields.Boolean("Configure Variants", default=False)
    attribute_ids = fields.One2many('configure.product.attribute', 'parent_id', string="Attributes")

    # explicitly pass in context
    def _default_pricelist_grid(self):
        p_id = self._default_product()
        price_grid_dict = p_id._build_price_grid(published_only=False)
        r_price_grid = self.env['product.pricelist.inquiry.grid.wizard']
        if price_grid_dict:
            for idx, qty in enumerate(price_grid_dict['quantities'], start=0):
                values = {
                    "catalog_pricelist": price_grid_dict['catalog_pricelist'],
                    "net_pricelist": price_grid_dict['net_pricelist'],
                    "quantity": qty,
                    "catalog_price": price_grid_dict['catalog_prices'][idx],
                    "net_price": price_grid_dict['net_prices'][idx],
                    "discount_code": price_grid_dict['discount_codes'][idx],
                    "start_date": price_grid_dict['effective_dates'][idx],
                    "end_date": price_grid_dict['expiration_dates'][idx],
                    "published": price_grid_dict['published'][idx],
                    "extra_price": price_grid_dict['price_extras'][idx],
                }
                r_price_grid |= self.env['product.pricelist.inquiry.grid.wizard'].create(values)
        return r_price_grid

    pricelist_grid_ids = fields.One2many('product.pricelist.inquiry.grid.wizard', 'product_id', string='Pricelist Grid Items', default=_default_pricelist_grid)

    @api.multi
    def get_extra_price_on_value(self):
        value_list = []
        p_id = self._default_product()
        price_grid_dict = p_id._build_price_grid(published_only=False)
        if price_grid_dict:
            for idx, qty in enumerate(price_grid_dict['quantities'], start=0):
                values = {
                    "catalog_pricelist": price_grid_dict['catalog_pricelist'],
                    "net_pricelist": price_grid_dict['net_pricelist'],
                    "quantity": qty,
                    "catalog_price": price_grid_dict['catalog_prices'][idx],
                    "net_price": price_grid_dict['net_prices'][idx],
                    "discount_code": price_grid_dict['discount_codes'][idx],
                    "start_date": price_grid_dict['effective_dates'][idx],
                    "end_date": price_grid_dict['expiration_dates'][idx],
                    "published": price_grid_dict['published'][idx],
                    "extra_price": price_grid_dict['price_extras'][idx],
                }
                value_list.append((0, 0, values))
        return value_list

    @api.onchange('attribute_ids', 'attribute_ids.value_id')
    def _onchange_attribute_value(self):
        for rec in self:
            if rec.attribute_ids.mapped('value_id'):
                values = self.with_context(
                    no_create_variant_attributes=rec.attribute_ids.mapped('value_id').ids).get_extra_price_on_value()
            else:
                values = self.get_extra_price_on_value()
            rec.pricelist_grid_ids = False
            rec.pricelist_grid_ids = values
