# -*- coding: utf-8 -*-
{
    'name': "TMG Sales Team Extensions",

    'summary': """
        Adds a many 2 many team id membership to Odoo""",

    'description': """
        The current sales team implementation only allows a user to be on one team. For
        TMG a user can be on multiple teams
    """,

    'author': "The Magnet Group",
    'website': "http://www.themagnetgroup.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['sales_team'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/tmg_salesteam_views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}