# -*- coding: utf-8 -*-
{
    'name': "tmg_stock_extensions",

    'summary': """ TMG Extensions to Stock and Delivery Modules """,

    'description': """
        Extensions to models, views and functions of Stock and Delivery functions based on TMG
        * Jonas Temple - 11/4/2020 - Added "Verify" function to inventory adjustment when no quantity change is
          required. Also added "last verified" fields to the stock.inventory.line model.  Added code to set the 
          inventory move dates with the accounting date if supplied.
    """,

    'author': "The Magnet Group",
    'website': "http://www.themagnetgroup.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Stock',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'stock'
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/tmg_delivery_templates.xml',
        'views/tmg_inventory_adjustment.xml',
        'report/tmg_stock_reports.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}