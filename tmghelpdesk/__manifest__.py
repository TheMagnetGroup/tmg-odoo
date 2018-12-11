# -*- coding: utf-8 -*-
{
    'name': "TMG Helpdesk Extensions",

    'summary': """
        Extends the Odoo Helpdesk module to check for tickets in the Urgent team that fails SLA policies
    """,

    'sequence' : 2,

    'description': """
        This TMG module checks for urgent tickets that have not been assigned within 15 minutes.
        If the ticket is not assigned a wider audience will be notified.
    """,

    'author': "The Magnet Group",
    'website': "http://www.themagnetgroup.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Helpdesk',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['helpdesk'],

    # always loaded
    'data': [
        'data/cron.xml',
        'views/tmg_helpdesk_views.xml'
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}