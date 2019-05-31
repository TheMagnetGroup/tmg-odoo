# -*- coding: utf-8 -*-
{
        "name": "Sales Order Hold",
    'summary': "Web",
    'description': """
Add sales holds to orders
""",
    "author": "Odoo Inc",
    'website': "https://www.odoo.com",
    'category': 'Sale',
    'version': '0.1',
    # any module necessary for this one to work correctly
    'depends': ['sale_management', 'sale_stock', 'mrp'],

    # always loaded
    'data': [
        'views/sale_hold_views.xml',
        'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}