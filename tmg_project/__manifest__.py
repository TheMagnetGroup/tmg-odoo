# -*- coding: utf-8 -*-
{
    'name': "TMG Project Extensions",

    'summary': """
        TMG extensions to the base Project module.
        """,

    'sequence': 2,

    'description': """
        Adds visibility to the task id, similar to how the Helpdesk module works.
        """,

    'author': "The Magnet Group",
    'website': "http://www.themagnetgroup.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Project',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['project'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/tmg_project_views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}