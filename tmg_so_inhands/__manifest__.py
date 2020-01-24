# -*- coding: utf-8 -*-
{
    'name': "TMG Sales Order In Hands",

    'summary': """
        TMG enhancements to the Sales module. Note that we have multiple modules that modify the Sales app, need
        to consider consolidating to one module.
        """,

    'description': """
        Adds an informational field, In-Hands Date to the Sales order and as a related field in the job and delivery order.
        * Jonas Temple - 2020/01/23 - Changes the base functionality of Odoo to allow editing of the commitment 
          date (ship date) when the order is in the confirmed state. 
    """,

    'author': "The Magnet Group",
    'website': "http://www.themagnetgroup.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sale',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['mrp_job' , "tmg_mrp", "sale"],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/sales_order.xml',
        'views/mrp_view.xml',
        'views/picking_view.xml'

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}