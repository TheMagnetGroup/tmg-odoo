# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp


class PriceList(models.Model):
    _inherit = 'product.pricelist'

    @api.multi
    def _compute_price_rule(self, products_qty_partner, date=False, uom_id=False):

        # Get the attributes that don't create variants
        # This will either be supplied by the overridden _get_combination_info or
        # by base Odoo when adding a line to an order
        no_create_variant_attribute_ids = self.env.context.get('no_create_variant_attributes')
        if not no_create_variant_attribute_ids:
            no_create_variant_attribute_ids = self.env.context.get('default_product_no_variant_attribute_value_ids')
            if no_create_variant_attribute_ids:
                no_create_variant_attribute_ids = [item[1] for item in no_create_variant_attribute_ids]

        # First call Odoo's base _compute_price_rule to get the price without applying price extras
        result = super(PriceList, self)._compute_price_rule(products_qty_partner, date=date, uom_id=uom_id)

        # If there were attribute ids that don't create variants
        if no_create_variant_attribute_ids:

            # result is a dictionary of product_id: [price, rule_id]
            for pid in result:
                # if there is a rule:
                if result[pid][1]:
                    rule_id = self.env['product.pricelist.item'].browse(result[pid][1])
                    # if the rule has extra ids:
                    if rule_id and rule_id.extra_ids:

                        d = {}
                        for e in rule_id.extra_ids:
                            # d[e.attribute_id] = set(e.value_ids), e.price_extra
                            for id in e.value_ids:
                                d[(e.attribute_id,id.id)] = e.price_extra

                        for id in no_create_variant_attribute_ids:
                            val = self.env['product.template.attribute.value'].browse(id)
                            # if val.attribute_id in d and val in d[val.attribute_id][0]:
                            if (val.attribute_id, val.product_attribute_value_id.id) in d:
                                result[pid] = result[pid][0] + d[(val.attribute_id,val.product_attribute_value_id.id)], result[pid][1]

        return result


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    product_tags_ids = fields.Many2many('product.template.tags', string='Product Tags')
    product_style_number = fields.Char(string='Product Style Number')

    _sql_constraints = [
        ('product_style_number_uniq',
         'UNIQUE (product_style_number)',
         'This Product Style Number is already used for another product'
         )
    ]

    @api.multi
    def _get_combination_info(self, combination=False, product_id=False, add_qty=1, pricelist=False, parent_combination=False, only_template=False):

        # Store attributes with no variants in the context
        if combination:
            no_create_variant_attributes = combination - combination._without_no_variant_attributes()
            self = self.with_context(no_create_variant_attributes=no_create_variant_attributes.ids)

        # Call the base method
        result = super(ProductTemplate, self)._get_combination_info(combination, product_id, add_qty, pricelist, parent_combination, only_template)


        return result

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    price_at_qty = fields.Float(string='Price At Quantity', digits=dp.get_precision('Product Unit of Measure'), required=True, default=0.0)

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):

        # First call Odoo's base _get_display_price to get the price without extra attribute pricing
        #result = super(SaleOrderLine, self).product_id_change()

        if not self.product_id:
            return {'domain': {'product_uom': []}}

        # remove the is_custom values that don't belong to this template
        for pacv in self.product_custom_attribute_value_ids:
            if pacv.attribute_value_id not in self.product_id.product_tmpl_id._get_valid_product_attribute_values():
                self.product_custom_attribute_value_ids -= pacv

        # remove the no_variant attributes that don't belong to this template
        for ptav in self.product_no_variant_attribute_value_ids:
            if ptav.product_attribute_value_id not in self.product_id.product_tmpl_id._get_valid_product_attribute_values():
                self.product_no_variant_attribute_value_ids -= ptav

        vals = {}
        domain = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            vals['product_uom'] = self.product_id.uom_id
            vals['product_uom_qty'] = self.product_uom_qty or 1.0

        product = self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id,
            quantity=vals.get('product_uom_qty') or self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id
        )

        result = {'domain': domain}

        name = self.get_sale_order_line_multiline_description_sale(product)

        vals.update(name=name)

        self._compute_tax_id()

        if self.order_id.pricelist_id and self.order_id.partner_id:
            vals['price_unit'] = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)
        self.update(vals)

        title = False
        message = False
        warning = {}
        if product.sale_line_warn != 'no-message':
            title = _("Warning for %s") % product.name
            message = product.sale_line_warn_msg
            warning['title'] = title
            warning['message'] = message
            result = {'warning': warning}
            if product.sale_line_warn == 'block':
                self.product_id = False

        # if there is a rule and it has extras
        if self.order_id.pricelist_id:

            products_qty_partner = [(self.product_id, self.price_at_qty or self.product_uom_qty, self.order_id.partner_id)]
            price_rule = self.order_id.pricelist_id._compute_price_rule(products_qty_partner)

            # If there was a rule
            if price_rule[self.product_id.id][1]:

                rule_id = self.env['product.pricelist.item'].browse(price_rule[self.product_id.id][1])

                if rule_id and rule_id.extra_ids:

                    price_extras = 0.0
                    vals = {}

                    # Create a dictionary to hold the attribute id/values and price extra
                    d = {}
                    for e in rule_id.extra_ids:
                        for x in e.value_ids:
                            d[(e.attribute_id, x.id)] = e.price_extra

                    # Check the product's attributes for price extra
                    if self.product_id.attribute_value_ids:
                        for val in self.product_id.attribute_value_ids:
                            if (val.attribute_id, val.id) in d:
                                price_extras = price_extras + d[(val.attribute_id,val.id)]

                    # Also check attributes that don't create variants for price extras
                    if self.product_no_variant_attribute_value_ids:
                        for val in self.product_no_variant_attribute_value_ids:
                            if (val.attribute_id, val.product_attribute_value_id.id) in d:
                                price_extras = price_extras + d[(val.attribute_id,val.product_attribute_value_id.id)]

                    price = self.price_unit + price_extras
                    vals['price_unit'] = self.env['account.tax']._fix_tax_included_price_company(price, self.product_id.taxes_id, self.tax_id, self.company_id)
                    self.update(vals)

        return result

    @api.onchange('product_uom', 'product_uom_qty', 'price_at_qty')
    def product_uom_change(self):

        # Set the variants that don't create attributes in the context
        self = self.with_context(no_create_variant_attributes=self.product_no_variant_attribute_value_ids.ids)
        # Call the base routine
        #super(SaleOrderLine, self).product_uom_change()

        #return result

        if not self.product_uom or not self.product_id:
            self.price_unit = 0.0
            return
        if self.order_id.pricelist_id and self.order_id.partner_id:
            product = self.product_id.with_context(
                lang=self.order_id.partner_id.lang,
                partner=self.order_id.partner_id,
                quantity=self.price_at_qty or self.product_uom_qty,
                date=self.order_id.date_order,
                pricelist=self.order_id.pricelist_id.id,
                uom=self.product_uom.id,
                fiscal_position=self.env.context.get('fiscal_position')
            )
            self.price_unit = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product),
                                                                                  product.taxes_id, self.tax_id,
                                                                                  self.company_id)


class tmg_product_pricelist_item(models.Model):
    _inherit = 'product.pricelist.item'

    extra_ids = fields.One2many('product.pricelist.item.extras', 'pricelist_item_id', string="Price Extras", copy=True)


class tmg_product_pricelist_item_extra(models.Model):
    _name = 'product.pricelist.item.extras'
    _description = "Pricelist Item Extras"

    pricelist_item_id = fields.Many2one(
        'product.pricelist.item','Product Pricelist Item', ondelete='cascade',
        help='The pricelist item this attribute extra price is associated with')

    price_extra = fields.Float(
        'Attribute Price Extra', digits=(10,2),
        help='The additional price this attribute extra adds to the product price')

    attribute_id = fields.Many2one('product.attribute', string='Attribute', ondelete='restrict', required=True)
    value_ids = fields.Many2many('product.attribute.value', string='Attribute Values')
