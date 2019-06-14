# -*- coding: utf-8 -*-
{
        "name": "TMG Sales Order Hold",
    'summary': "Creates a new sale.hold module for the sale order.",
    'description': """
Add sales holds to orders that can block production or delivery. Also implements a credit check on the sales order to place orders on credit hold under certain conditions
""",
    "author": "The Magnet Group",
    'website': "http://www.themagnetgroup.com",
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