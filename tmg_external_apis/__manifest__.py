# -*- coding: utf-8 -*-
{
    'name': "TMG External API",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,
    "application": True,
    'author': "TheMagnetGroup",
    'website': 'https://www.odoo.com',
    'license': 'LGPL-3',
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales',
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