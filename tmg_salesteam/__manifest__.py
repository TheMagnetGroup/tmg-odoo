# -*- coding: utf-8 -*-
{
    'name': "TMG Sales Team Extensions",

    'summary': """
        Adds a many 2 many team id membership to Odoo""",

    'description': """
        The current sales team implementation only allows a user to be on one team. For
        TMG a user can be on multiple teams
        * Anoop C S    - 2021/08/13 -   Added option for mass update the contact's sales team 
    """,

    'author': "The Magnet Group",
    'website': "http://www.themagnetgroup.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales',
    'version': '12.1.2',

    # any module necessary for this one to work correctly
    'depends': [
        'sale',
        'sales_team',
        'crm',
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/tmg_salesteam_views.xml',
        'views/templates.xml',
        'wizard/notification_wizard_view.xml',
        'wizard/mass_sales_team_update_wizard_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}