# -*- coding: utf-8 -*-
{
    'name': "tmg_sale",

    'summary': """
        Main module used to modify basic functions of the sale module.""",

    'description': """
        We will use this to encompass modifications to SALE that are mainly focused on the SALE branch without the need to create new tmg modules
    """,

    'author': "The Magnet Group",
    'website': "http://www.themagnetgroup.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sale',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/sale_views.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}