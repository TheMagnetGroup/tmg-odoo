# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    "name": "Manufacturing JOB: Multiple MO processing",
    'summary': "Web",
    'description': """
Manufacturing JOB: Muliple MO processing
""",
    "author": "Odoo Inc",
    'website': "https://www.odoo.com",
    'category': 'Manufacturing',
    'version': '0.1',
    'depends': ['mrp', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/mrp_job_views.xml',
        'views/sale_order_views.xml'
    ],
    'license': 'OEEL-1',
}
