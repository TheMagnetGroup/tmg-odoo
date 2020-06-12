# -*- coding: utf-8 -*-

from odoo import models, api, fields
# from lxml import objectify


class inventory(models.Model):
    _name = 'tmg_external_api.inventory'
    _description = 'Serve product inventory availability information'

    _product_template_id = fields.Integer(0)
    # _product_bom_id = fields.Integer(0)

# ------------------
#  Public functions
# ------------------

    @api.model
    def Inventory(self, style_rqs, colors_rqs):

        if not style_rqs:
            return []

        # original_rqs = objectify.fromstring(soap_request_parms)
        # # original_rqs = json.loads(soap_request_parms)
        # u_name = original_rqs['Request']['id']
        # consumer_id = fields.Integer()
        # partner_search = [('name', '=', u_name)]
        # consumer_id = self.env['res.users'].search_read(partner_search, ['partner_id'])
        #
        # prostd_obj = self.env["tmg_external_api.promostandards"]
        # prostd_obj.log_transaction(consumer_id[0]['partner_id'][0], soap_request_parms, self._name)

        inventory._product_template_id = 0
        # inventory._product_bom_id = 0
        not_component = False

        product_style_search = [
            ('product_style_number', '=', style_rqs),
            ('active', '=', True),
            ('product_tmpl_id.sale_ok', '=', True)
        ]
        if colors_rqs:
            product_style_search.append(
                ('attribute_value_ids', 'in', self._get_attribute_id(colors_rqs))
            )
        variant_list = self._get_product_inventory(product_style_search, not_component)

        # 2020-06-02 jbergt - Bill of Material items will be ignored for inventory until otherwise notified
        # bom_search = [
        #     ('active', '=', True),
        #     ('id', '=', inventory._product_bom_id)
        #     # ('parent_product_tmpl_id', '=', inventory.product_template_id)
        # ]
        # variant_list = self._append_components_inventory(bom_search, variant_list)

        return variant_list

    @api.model
    def InventoryFilterValues(self, style_rqs):

        if not style_rqs:
            return []
        product_style_search = [
            ('product_style_number', '=', style_rqs),
            ('active', '=', True),
            ('product_tmpl_id.sale_ok', '=', True)
        ]
        field_list = ['attribute_value_ids']
        product_data = self.env['product.product'].search_read(product_style_search, field_list)
        variant_attribute_name_list = []
        for pd in product_data:
            attrname = self._get_attribute_name(pd['attribute_value_ids'])
            if attrname and not variant_attribute_name_list.__contains__(attrname):
                variant_attribute_name_list.append(attrname)
        return variant_attribute_name_list

# -------------------
#  Private functions
# -------------------

    @api.model
    def _get_product_inventory(self, product_search, is_component):
        product_inventory_data = []
        field_list = [
            'id',
            'name',
            'default_code',
            'qty_available',
            'attribute_value_ids',
            'outgoing_qty',
            'virtual_available_qty',
            'product_tmpl_id',
            'product_style_number',
            'bom_id',
            'bom_ids'
        ]
        product_data = self.env['product.product'].search_read(product_search, field_list)
        for pd in product_data:
            color = self._get_attribute_name(pd['attribute_value_ids'])
            expected = self._get_earliest_expected(pd['default_code'])
            data = dict(
                isComponent=is_component,
                styleNumber=pd['product_style_number'],
                nameProduct=pd['name'],
                idVariant=pd['default_code'],
                qtyAvailable=pd['qty_available'],
                qtyOutgoing=pd['outgoing_qty'],
                netAvailable=(pd['virtual_available_qty']),
                nameColor=color or '',
                descriptionVariant=pd['name'] + ((' - ' + color) if color else ''),
                dateScheduled=(expected['scheduled_date_str'] if 'scheduled_date_str' in expected else ''),
                qtyProductUom=(expected['product_uom_qty'] if 'product_uom_qty' in expected else 0)
            )
            product_inventory_data.append(data)
            if inventory._product_template_id == 0:
                inventory._product_template_id = pd['product_tmpl_id'][0]
                # if pd['bom_id']:
                #     inventory._product_bom_id = pd['bom_id'][0]
        return product_inventory_data

    # 2020-06-02 jbergt - Bill of Material items will be ignored for inventory until otherwise notified
    # @api.model
    # def _append_components_inventory(self, bom_search, component_inventory_data):
    #     bom_fields = [
    #         'bom_line_ids',
    #         'product_tmpl_id'
    #     ]
    #     bom_data = self.env['mrp.bom'].search_read(bom_search, bom_fields)
    #     for bd in bom_data:
    #         component_search = [
    #             ('id', 'in', bd['bom_line_ids'])
    #         ]
    #         component_fields = [
    #             'product_tmpl_id',
    #             'product_id',
    #             'bom_id',
    #             'id'
    #         ]
    #         component_data = self.env['mrp.bom.line'].search_read(component_search, component_fields)
    #         for cd in component_data:  # first element should be only one:
    #             component_product_search = [
    #                 ('id', '=', cd['product_id'][0]),
    #                 ('active', '=', True)
    #                 # ('active', '=', True),
    #                 # ('product_tmpl_id.sale_ok', '=', True)
    #             ]
    #             is_component = True
    #             product_data = self._get_product_inventory(component_product_search, is_component)
    #             if product_data:
    #                 # potentially a list/dict but here filtered to single product; "pop" the one list element
    #                 component_inventory_data.append(product_data.pop(0))
    #     return component_inventory_data

    @api.model
    def _get_attribute_name(self, attrid=None):
        if not attrid:
            return ''
        else:
            attribute_search = [('id', 'in', attrid)]
            attributename = self.env['product.attribute.value'].search_read(attribute_search, ['name'])
            return attributename[0]['name']

    @api.model
    def _get_attribute_id(self, attrname=None):
        if not attrname:
            return 0
        else:
            attribute_search = [('name', 'in', attrname)]
            attributeids = self.env['product.attribute.value'].search_read(attribute_search, ['attribute_id'])
            id_list = []
            for ai in attributeids:
                id_list.append(ai['id'])
            return id_list

    @api.model
    def _get_earliest_expected(self, defaultcode=None):
        if not defaultcode:
            return dict()
        else:
            # retrieve incoming scheduled stock that is pending (i.e. not in the "not pending" status list)
            status_not_pending = ['done', 'draft']
            expected_stock_search = [
                ('product_id', '=', defaultcode),
                ('picking_id.picking_type_id.code', '=', 'incoming'),
                ('state', 'not in', status_not_pending)
            ]
            field_list = [
                'product_id',
                'id',
                'state',
                'scheduled_date',
                'product_uom_qty'
            ]
            expected_stock = self.env['stock.move.line'].search_read(expected_stock_search, field_list)
            earliest_expected = dict()
            if expected_stock:
                # select the earliest scheduled incoming stock qty
                expected_stock.sort(key=lambda d: d['scheduled_date'])
                earliest_expected = dict(
                    scheduled_date_str=fields.Date.to_string(expected_stock[0]['scheduled_date']),
                    product_uom_qty=expected_stock[0]['product_uom_qty']
                )
            return earliest_expected
