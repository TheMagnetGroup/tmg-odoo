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
                    # If there was a rule id then append the discount code, start date and end date to the result
                    # if rule_id:
                    #     result[pid].append(rule_id.discount_code)
                    #     result[pid].append(rule_id.date_start)
                    #     result[pid].append(rule_id.date_end)

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

    def get_product_published_quantities(self, product, date=False):
        # Get the published quantities for a product template. Note that this routine does
        # not support quantities for a product.product or product category, only a product template
        if not date:
            date = self._context.get('date') or fields.Date.today()
        date = fields.Date.to_date(date)  # boundary conditions differ if we have a datetime
        self._cr.execute(
            'SELECT item.min_quantity '
            'FROM product_pricelist_item AS item '
            'WHERE (item.product_tmpl_id = %s)'
            'AND (item.pricelist_id = %s) '
            'AND (item.date_start IS NULL OR item.date_start<=%s) '
            'AND (item.date_end IS NULL OR item.date_end>=%s) '
            'AND (item.published = True) '
            'ORDER BY item.min_quantity',
            (product.id, self.id, date, date))
        return [x[0] for x in self._cr.fetchall()]


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    product_tags_ids = fields.Many2many('product.template.tags', string='Product Tags')
    depth = fields.Float(string='Product Depth')
    width = fields.Float(string='Product Width')
    height = fields.Float(string='Product Height')
    dimensions = fields.Char(string='Dimensions', compute='_compute_dimensions', store=False)
    primary_material = fields.Char(string='Primary Material')
    market_introduction_date = fields.Date(string='Market Introduction Date')
    warehouses = fields.Many2many('stock.warehouse', string='Warehouses')
    data_last_change_date = fields.Date(string='Data Last Change Date')
    ala_catalog = fields.Float(string='As Low As Catalog', compute='_compute_ala')
    ala_net = fields.Float(string='As Low As Net', compute='_compute_ala')
    ala_code = fields.Char(string='As Low As Code', compute='_compute_ala')
    product_style_number = fields.Char(string='Product Style Number', copy=False)

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

    @api.depends('depth', 'width', 'height')
    def _compute_dimensions(self):
        for product in self:
            dimensions = None
            if product.depth and product.width and product.height:
                dimensions = "{width:.2f}\" x {height:.2f}\" x {depth:.2f}\"".format(width=product.width, height=product.height, depth=product.depth)
            product.dimensions = dimensions

    @api.multi
    def _compute_ala(self):
        for product in self:
            pricingGrid = product._build_price_grid()
            if pricingGrid:
                product.ala_catalog = pricingGrid[1][-1]
                product.ala_net = pricingGrid[2][-1]
                product.ala_code = pricingGrid[3][-1]
            else:
                product.ala_catalog = None
                product.ala_net = None
                product.ala_code = None

    # This routine returns a dictionary with prices from 2 different priceslists with the intention that the first
    # pricelist is catalog and the second pricelist is net.  The default functionality is to return
    # prices from priceslists named specifically 'Catalog' and 'Net'.  The dictionary structure is:
    #   {
    #       "catalog_pricelist" : "name",
    #       "catalog_currency" : "name",
    #       "net_pricelist" : "name",
    #       "net_currency" : "name",
    #       "quantities" : [list_of_quantities],
    #       "catalog_prices" : [list_of_prices],
    #       "net_prices" : [list_of_prices],
    #       "discount_codes" : [list_of_discount_codes],
    #       "effective_dates" : [list_of_dates],
    #       "expiration_dates" : [list_of_dates]
    #   }
    def _build_price_grid(self, catalog_pricelist='Catalog', net_pricelist='Net'):
        # Get the passed catalog/net pricelists or the default
        cat = self.env['product.pricelist'].search([('name', '=', catalog_pricelist)])
        net = self.env['product.pricelist'].search([('name', '=', net_pricelist)])
        price_grid_dict = {}
        cat_prices = []
        net_prices = []
        discount_codes = []
        effective_dates = []
        expiration_dates = []
        # If we have both
        if cat and net:
            for product in self:
                # Get the published quantities from the catalog pricelist, assuming current date as effectivity
                quantities = cat.get_product_published_quantities(product)
                price_grid_dict['catalog_pricelist'] = cat.name
                price_grid_dict['catalog_currency'] = cat.currency_id.name
                price_grid_dict['net_pricelist'] = net.name
                price_grid_dict['net_currency'] = net.currency_id.name
                price_grid_dict['quantities'] = quantities
                for qty in quantities:
                    cat_price = cat.get_product_price_rule(self, qty, None)
                    cat_prices.append(cat_price[0])
                    net_price = net.get_product_price_rule(self, qty, None)
                    net_prices.append(net_price[0])
                    # Get the rule ID that generated this pricing
                    pi = self.env['product.pricelist.item'].browse(net_price[1])
                    if pi:
                        discount_codes.append(pi.discount_code)
                        effective_dates.append(pi.date_start)
                        expiration_dates.append(pi.date_end)

                price_grid_dict['catalog_prices'] = cat_prices
                price_grid_dict['net_prices'] = net_prices
                price_grid_dict['discount_codes'] = discount_codes
                price_grid_dict['effective_dates'] = effective_dates
                price_grid_dict['expiration_dates'] = expiration_dates

                    # if net_price[1]:
                        # pi = product.env['product.pricelist.item'].browse(net_price[1])
                        # discount_codes.append(pi.discount_code)
                        # price_effective_dates.append(pi.date_start)
                        # price_effective_dates.append(pi.date_end)
            #return [quantities, catalog_pricelist, cat_prices, net_pricelist, net_prices, discount_codes, price_effective_dates, price_expiration_dates]
            return price_grid_dict


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
    discount_code = fields.Selection([
        ('A', 'A - 50% Discount'),
        ('B', 'B - 45% Discount'),
        ('C', 'C - 40% Discount'),
        ('D', 'D - 35% Discount'),
        ('E', 'E - 30% Discount'),
        ('F', 'F - 25% Discount'),
        ('G', 'G - 20% Discount'),
        ('H', 'H - 15% Discount'),
        ('X', 'X - 0% Discount'),
        ('Z', 'Z - 100% Discount'),
        ], string='Discount Code')
    published = fields.Boolean(string='Published', help="Published pricing shows on our external website, ESP, SAGE, etc.",
                               default=True)


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
