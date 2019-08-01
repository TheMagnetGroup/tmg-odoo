# -*- coding: utf-8 -*-
{
    'name': "TMG customer extensions",

    'summary': """
        TMG customer extensions""",

    'description': """
        Add bool field to res.partner named "Rebate". 
        Add "Rebate" field to res.partner form view but only show the field if "Is Customer" is true
    """,

    'author': "The Magnet Group",
    'website': "http://www.themagnetgroup.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/tmg_customer_views.xml',
       # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}