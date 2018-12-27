# -*- coding: utf-8 -*-
{
    'name': "TMG Stock Picking Batch Extensions",

    'summary': """
        Extends the stock picking batch Odoo base addon module with:
            * Modify the stock picking batch report
       """,

    'description': """
        TMG modified the stock picking batch report to replace the pick id text with a barcode
    """,

    'author': "The Magnet Group",
    'website': "http://www.themagnetgroup.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Inventory',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'report/tmg_report_picking_batch.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}