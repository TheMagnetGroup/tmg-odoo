# -*- coding: utf-8 -*-
{
    'name': 'TMG: mrp',
    'summary': "The Magnet Group: Link SO-line to MO",
    'description':
    """
    We need to create a unique link between an SO-line and the MO it creates through MTO.
    """,
    'license': 'OEEL-1',
    'author': 'Odoo Inc',
    'version': '0.1',
    'depends': ['sale_stock', 'sale_management', 'mrp'],
    'data': [
        'views/mrp_production_views.xml',
        'views/sale_order_views.xml',

    ],
}