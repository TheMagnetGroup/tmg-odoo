# -*- coding: utf-8 -*-
{
    'name': "TMG Sales Order",

    'summary': """
        Adds TMG fields and functions to sale.order""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Christian Dunn",
    'website': "http://www.themagnetgroup.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale', 'stock_account', 'mrp', 'tmg_mrp_production'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}