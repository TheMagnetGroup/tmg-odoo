# -*- coding: utf-8 -*-
{
    'name': "tmg_stock_rule",

    'summary': """
        TMG Mods on stock_rule """,

    'description': """
        Modifications made my TMG on the odoo module stock_rule
    """,

    'author': "TheMagnetGroup",
    'website': "http://www.themagnetgroup.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Production',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale_stock',  ],

    # always loaded
    #'data': [
    #],
    # only loaded in demonstration mode
    #'demo': [
    #],
}