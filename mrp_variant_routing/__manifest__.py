# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    "name": "Mrp Variant Routings: Workorders based on variant attributes",
    'summary': "Web",
    'description': """
Mrp Variant Routings: Workorders based on variant attributes
============================================================
- Workorders based on non active variants on manufacturing orders.
- Idea to have a single routing for multiple manufacturing processes.
""",
    "author": "Odoo Inc",
    'website': "https://www.odoo.com",
    'category': 'Manufacturing',
    'version': '0.1',
    'depends': ['mrp', 'mrp_bom_extended'],
    'data': [
        'views/mrp_routing_workcenter_views.xml'
    ],
    'license': 'OEEL-1',
    'application': True,
    'cloc_exclude': ['**/*'],
}
