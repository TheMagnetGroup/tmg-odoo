# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': "IOT Printing",
    'version': '1.0',
    'depends': ['delivery', 'iot'],
    'author': 'Odoo Inc',
    'maintainer': 'Odoo Inc',
    'category': 'Tools',
    'license': 'OEEL-1',
    'description': """
IOT Printing
============
- Print delivery labels directly to the printer connected to IOT Box.
    """,
    # data files always loaded at installation
    'data': [
        'views/assets.xml',
        'views/delivery_carrier_views.xml',
        'views/iot_device_views.xml',
        'views/stock_picking_views.xml'
    ],
    'cloc_exclude': ['**/*'],
}
