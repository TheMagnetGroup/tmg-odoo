# -*- coding: utf-8 -*-
{
    'name': "TMG External API",

    'summary': """
        Contains logging and odoo functions for APIs""",

    'description': """
        * Christian Dunn - 2020/05/29 -   Initial Commit
        * Jon W. Bergt - 2020-06-11 -  Updated to include requirements for Inventory API
        * Jonas Temple - 2020/08/12 -  Added export account model and views to store credentials for sending item information
    """,

    'author': "The Magnet Group",
    'website': "http://www.themagnetgroup.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['tmg_sale',
                'sales_margin_percentage',
                'tmg_product'
                ],
    # always loaded
    'data': [
        'data/cron.xml',
        "security/ir.model.access.csv",
        'views/views.xml',
        'views/templates.xml',
        'views/resPartner.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
