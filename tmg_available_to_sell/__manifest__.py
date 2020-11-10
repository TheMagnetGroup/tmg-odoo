# -*- coding: utf-8 -*-
{
    'name': "TMG Add Available Quantity",

    'summary': """
        Adds a new field labeled "Available Quantity" that calculates (Quantity On Hand - Outgoing)
        """,

    'description': """
        * Bridgette Cowden - 1/1/2020 - Adds computed field labeled "Available Quantity" 
            (technical name virtual_available_qty) with the formula Quantity On Hand - Outgoing. 
            Replaces the "Forecasted" stat button on the product detail form.
        * Jonas Temple - 11/10/2020 - Added virtual_available_qty to the product kanban and tree view,
            removed the on hand quantity which was only the finished good availability.
    """,

    'author': "The Magnet Group",
    'website': "http://www.themagnetgroup.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale_stock'],

    # always loaded
    'data': [
        'views/tmg_available_to_sell_views.xml',
    ],
}