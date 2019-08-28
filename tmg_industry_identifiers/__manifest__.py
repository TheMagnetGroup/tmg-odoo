# -*- coding: utf-8 -*-
{
    'name': "tmg_industry_identifiers",

    'summary': """
        Adds industry identifiers tab to customer (partner form)""",

    'description': """
        Add the following fields to the res.partner model: ASI Number, SAGE Number, PPAI Number
        Add a new notebook page labeled "Industry Identifiers" to the partner form
        Add the new fields to the new notebook page
    """,

    'author': "The Magnet Group",
    'website': "http://www.themagnetgroup.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale'],

    # always loaded
    'data': [
        'views/tmg_industry_identifiers_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
       # 'demo/demo.xml',
    ],
}