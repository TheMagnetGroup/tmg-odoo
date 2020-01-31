# -*- coding: utf-8 -*-
{
    'name': "tmg in hands date",

    'summary': """
        Replace the "Expected Date" with the "In Hands Date" on the sale order list""",

    'description': """
        * Bridgette Cowden - 1/31/2020 - Replace the "Expected Date" (expected_date on sale.order) with the 
            "In Hands Date" (in_hands on sale.order) on the sale order list.
    """,

    'author': "The Magnet Group",
    'website': "http://www.themagnetgroup.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/tmg_in_hands_views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}