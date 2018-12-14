# -*- coding: utf-8 -*-
{
    'name': "tmg_mrp_production",

    'summary': """
        Extends the Odoo Production Module to add a more direct relationship from the Sales.Line to the production Order.""",



    'description': """
        This TMG module creates a relationship to the SalesLine to access information such as Sales Order Notes.
    """,

    'author': "The Magnet Group",
    'website': "http://www.themagnetgroup.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Production',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['mrp',
        'sale',
        'sale_stock',
        'stock',
        ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        #'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
