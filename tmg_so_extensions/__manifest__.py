# -*- coding: utf-8 -*-
{
    'name': "TMG Sales Order Extensions",

    'summary': """
        Extend various properties and functions of Sales Order to better accommodate TMG business rules""",

    'description': """
        Extend various properties and functions of Sales Order to better accommodate TMG business rules""",

    'author': "The Magnet Group",
    'website': "http://www.themagnetgroup.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sale',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'sale'
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/tmg_sale_order_extensions_views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}