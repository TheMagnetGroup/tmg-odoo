# -*- coding: utf-8 -*-
{
    'name': "TMG External API",

    'summary': """
        Module to contain all APIs developed by TMG""",

    'description': """
        Creates a framework for logging, execution, and visibility for External APIs from The Magnet Group
    """,
    "application": True,
    'author': "The Magnet Group",
    'website': "http://www.themagnetgroup.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'sale',
    'version': '0.1',

    # any module necessary for this one to work correctly
      'depends': ['tmg_so_inhands', 'tmg_sale','sales_margin_percentage'],

    # always loaded
    'data': [
        'data/cron.xml',
        "security/ir.model.access.csv",
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}