# -*- coding: utf-8 -*-
{
    'name': "TMG Sale",

    'summary': """
        Main module used to modify basic functions of the sale module.""",

    'description': """
        * ??? - ??? - Adds pre-set search filter for Customer Reference (PO Number)
        * Jonas Temple - 2020/01/10 -   Adds In Hands Date and Ship Date (commitment_date) to the sale.report model. 
                                        Add Decoration Method to sale.order.line to record primary decoration method.
                                        Add Decoration Method to the sale.report model
        * Christian Dunn - 2020/01/27 -   Adds wizard to allow user to change ship date on MO, SO, and
        * Jonas Temple - 2020/01/23 -   Add On Hold and On Production Hold to the sale.report model.
        * Christi Moses - 2020/09/01    Add delivery method to sale order report
        * Christian Dunn - 2021/05/25    Add quick ship to order and order line
    """,

    'author': "The Magnet Group",
    'website': "http://www.themagnetgroup.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sale',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'tmg_mrp'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'wizard/ship_date_assign_wizard_view.xml',
        'views/sale_views.xml',
        'report/tmg_sale_reports.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
