# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    quick_ship = fields.Boolean("Quick Ship Order")

    @api.multi
    @api.depends('order_line')
    def _compute_quick_ship(self):
        for record in self:
            if any(l.quick_ship and l.product_uom_qty > l.qty_invoiced for l in record.order_line):
                record.quick_ship = True
            else:
                record.quick_ship = False


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    decoration_method = fields.Char('Decoration Method', compute='_get_deco_method', store=True, help='Decoration method used on the sale order line')
    quick_ship = fields.Boolean(string="Quick Ship")
    # printed_date = fields.Datetime(string="Date")
    material_cost = fields.Float('Material Cost')
    labor_cost = fields.Float('Labor Cost')
    overhead_cost = fields.Float('Overhead Cost')




        # if any(l.quick_ship and l.product_uom_qty > l.qty_invoiced for l in self.order_id.order_line):
        #     self.order_id.quick_ship = True
        # else:
        #     self.order_id.quick_ship = False

    @api.multi
    def write(self, vals):

        res = super(SaleOrderLine, self).write(vals)
        for record in self:
            if vals.get('quick_ship') is not None:
                # data = vals.get('quick_ship')

                if any(l.quick_ship and l.product_uom_qty > l.qty_invoiced for l in record.order_id.order_line):
                    record.order_id.quick_ship = True
                else:
                    record.order_id.quick_ship = False
        return res



    # @api.multi
    # @api.onchange('quick_ship')
    # def _compute_quick_ship(self):
    #     for record in self:
    #         if any(l.quick_ship and l.product_uom_qty > l.qty_invoiced for l in record.order_id.order_line):
    #             record.order_id.quick_ship = True
    #         else:
    #             record.order_id.quick_ship = False


    @api.multi
    @api.depends('product_no_variant_attribute_value_ids')
    def _get_deco_method(self):
        """ Calculate the decoration method for this sale order line
            * decoration_method - stores the decoration method used on the order line
        """

        for line in self:
            for attribute in line.product_no_variant_attribute_value_ids:
                if attribute.attribute_id.name.strip() == "Decoration Method":
                    line.decoration_method = attribute.name

    # This function returns a list of lists that has the lines on the BOM that apply to the
    # product passed, based on both variants that create attributes and variants that do not create
    # attributes.  Each list contains:
    #   product id from the bom line
    #   quantity from the bom line
    #   cost of the product id from the bom line
    #   extended cost based on the quantity * cost
    #   cost type which can be material, labor, overhead or scrap
    def _get_bom_cost_detail(self, product_id):
        mtl = 0.0
        lab = 0.0
        scrap = 0.0
        ovh_pct = 0
        scrap_pct = 0.0
        include_line = False
        cost_detail = []
        cost = 0.0
        cost_type = None

        # Get the non-variant creating attribute IDs
        ptav = []
        for av in self.product_no_variant_attribute_value_ids:
            ptav.append(av.product_attribute_value_id.id)

        for line in product_id.product_tmpl_id.bom_id.bom_line_ids:
            include_line = False
            # Determine if the line should be included in cost calculation
            if line.attribute_value_ids:
                if (set(self.product_id.attribute_value_ids.ids) & set(line.attribute_value_ids.ids) or
                    set(ptav) & set(line.attribute_value_ids.ids)):
                    include_line = True
            else:
                include_line = True
            # If cost should be included
            if include_line:
                # Products of type 'product' (Storeable Product) or 'consu' (Consumable) will be added to the material bucket
                if line.product_id.product_tmpl_id.type == 'product' or line.product_id.product_tmpl_id.type == 'consu':
                    cost_type = 'material'
                    cost = (line.product_id.standard_price * line.product_qty)
                    mtl += cost
                    cost_detail.append([line.product_id, line.product_qty, line.product_id.standard_price, cost, cost_type])
                # Products marked with 'labor' cost calc type will be added to the labor bucket
                elif line.product_id.product_tmpl_id.cost_calc_type == 'labor':
                    cost_type = 'labor'
                    cost = (line.product_id.standard_price * line.product_qty)
                    lab += cost
                    cost_detail.append([line.product_id, line.product_qty, line.product_id.standard_price, cost, cost_type])
                # Take the first product marked as using overhead cost calc
                # with an overhead percent as the overhead percentage amount to be applied.
                elif (line.product_id.product_tmpl_id.cost_calc_type == 'overhead' and
                        line.product_id.product_tmpl_id.overhead_percent != 0 and
                        ovh_pct == 0):
                    ovh_pct = line.product_id.product_tmpl_id.overhead_percent
                # Take the first product marked as using scrap cost calc
                # with an overhead percent as the overhead percentage amount to be applied.
                elif (line.product_id.product_tmpl_id.cost_calc_type == 'scrap' and
                        line.product_id.product_tmpl_id.scrap_percent != 0 and
                        scrap_pct == 0):
                    scrap_pct = line.product_id.product_tmpl_id.scrap_percent

        # Now add the overhead and scrap lines
        ovh = lab * (ovh_pct/100)
        cost_detail.append([None, None, None, ovh, 'overhead'])
        scrap = mtl * (scrap_pct/100)
        cost_detail.append([None, None, None, scrap, 'scrap'])

        return cost_detail

    def _compute_bom_cost(self, product_id):
        mtl = 0.0
        lab = 0.0
        ovh = 0.0

        # Get the bom cost detail
        cost_detail = self._get_bom_cost_detail(product_id)

        # Accumulate material, labor and overhead
        for cost_line in cost_detail:
            if cost_line[4] == 'material':
                mtl += cost_line[3]
            elif cost_line[4] == 'labor':
                lab += cost_line[3]
            elif cost_line[4] == 'overhead':
                ovh += cost_line[3]
            elif cost_line[4] == 'scrap':
                mtl += cost_line[3]

        return [mtl, lab, ovh]

    def _compute_margin(self, order_id, product_id, product_uom_id):
        frm_cur = self.env.user.company_id.currency_id
        to_cur = order_id.pricelist_id.currency_id
        if product_id.product_tmpl_id.bom_id:
            # Get the bom cost
            cost = self._compute_bom_cost(self.product_id)
            self.material_cost = cost[0]
            self.labor_cost = cost[1]
            self.overhead_cost = cost[2]
            purchase_price = sum(cost)
        else:
            purchase_price = product_id.standard_price
        if product_uom_id != product_id.uom_id:
            purchase_price = product_id.uom_id._compute_price(purchase_price, product_uom_id)
        price = frm_cur._convert(
            purchase_price, to_cur, order_id.company_id or self.env.user.company_id,
            order_id.date_order or fields.Date.today(), round=False)
        return price

    @api.model
    def _get_purchase_price(self, pricelist, product, product_uom, date):
        frm_cur = self.env.user.company_id.currency_id
        to_cur = pricelist.currency_id
        if product.product_tmpl_id.bom_id:
            purchase_price = sum(self._compute_bom_cost(product))
        else:
            purchase_price = product.standard_price
        if product_uom != product.uom_id:
            purchase_price = product.uom_id._compute_price(purchase_price, product_uom)
        price = frm_cur._convert(
            purchase_price, to_cur,
            self.order_id.company_id or self.env.user.company_id,
            date or fields.Date.today(), round=False)
        return {'purchase_price': price}


class ProductCategory(models.Model):
    _inherit = 'product.category'

    overhead_percent = fields.Float(string="Overhead Percent", help='Percentage of labor used to calculate overhead cost')
    scrap_percent = fields.Float(string="Scrap Percent", help='Percentage of material used to calculate scrap cost')


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    cost_calc_type = fields.Selection([
            ('labor', 'Labor'),
            ('overhead', 'Overhead'),
            ('scrap', 'Scrap')
        ], string="Cost Calculation Type")
    overhead_percent = fields.Float(string="Overhead Percent", compute="_get_overhead_percent", stored=True)
    scrap_percent = fields.Float(string="Scrap Percent", compute="_get_scrap_percent", stored=True)

    def _get_overhead_percent(self):
        for product in self:
            # The overhead percent will come from the most specific to least specific product category
            cat = product.categ_id
            while cat:
                if cat.overhead_percent:
                    product.overhead_percent = cat.overhead_percent
                    break
                cat = cat.parent_id

    def _get_scrap_percent(self):
        for product in self:
            # The scrap percent will come from the most specific to least specific product category
            cat = product.categ_id
            while cat:
                if cat.scrap_percent:
                    product.scrap_percent = cat.scrap_percent
                    break
                cat = cat.parent_id

    @api.onchange('purchase_ok', 'sale_ok', 'cost_calc_type', 'type')
    def _onchange_cost_type(self):
        """ Ensure that if the cost calc type has been set that the product is a service and cannot be purchased or sold
        """
        if self.cost_calc_type and (self.type != 'service' or self.sale_ok or self.purchase_ok):
            raise ValidationError(
                _("If the cost calc type is set then the product must be a service and cannot be sold or purchased."))

class BOMLine(models.Model):
    _inherit = 'mrp.bom.line'

    cost = fields.Float(compute="_get_line_cost", store=False, name='Cost')
    calc_percent = fields.Float(compute="_get_calc_percent", store=False, name='Cost Calc %')

    def _get_line_cost(self):
        for line in self:
            line.cost = line.product_id.standard_price

    def _get_calc_percent(self):
        for line in self:
            if not line.product_id.cost_calc_type or line.product_id.cost_calc_type == 'labor':
                line.calc_percent = 0
            elif line.product_id.cost_calc_type == 'overhead':
                line.calc_percent = line.product_id.overhead_percent
            elif line.product_id.cost_calc_type == 'scrap':
                line.calc_percent = line.product_id.scrap_percent