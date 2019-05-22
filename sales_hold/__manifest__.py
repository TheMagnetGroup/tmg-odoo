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
    'depends': ['base', 'sale_stock',],

    # always loaded
    'data': [
        'views/sale_hold_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}