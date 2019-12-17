# -*- coding: utf-8 -*-
{
    'name': "TMG Purchasing",

    'summary': """
        TMG Extensions to Odoo Purchasing""",

    'description': """
        Extends the Odoo purchasing module with TMG extensions
    """,

    'author': "The Magnet Group",
    'website': "http://www.themagnetgroup.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Purchase',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['purchase'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/tmg_purchase.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}