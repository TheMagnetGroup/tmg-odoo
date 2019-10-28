# -*- coding: utf-8 -*-
{
    'name': "TMG Import Delivery",

    'summary': "Gives the user the ability to enter individual delivery orders and adds 3rd party fedex.",
    'description': """
    Adds the ability to add a third party shipper number for fedex deliveries and adds to tmg_sale_stock's ability to enter bulk shipments by adding the ability to enter individual shipments in wizard
    """,

    "author": "The Magnet Group",
    'website': "http://www.themagnetgroup.com",
    'category': 'Sale',
    'version': '0.1',
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list

    # any module necessary for this one to work correctly
    'depends': [ 'tmg_sale_stock','tmg_mrp','delivery_ups'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',

        'wizard/sale_order_line_delivery_entry_wizard.xml',
        'views/views.xml',
        'views/picking_view.xml',
        'views/fedex_provider_view.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}