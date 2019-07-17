# -*- coding: utf-8 -*-
{
    'name': "TMG Sales Order In Hands",

    'summary': """
        Adds In-Hands date to the Sales Order""",

    'description': """
        Adds an informational field, In-Hands Date to the Sales order and as a related field in the job and delivery order.
    """,

    'author': "The Magnet Group",
    'website': "http://www.themagnetgroup.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sale',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['mrp_job' , "tmg_mrp",],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/sales_order.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}