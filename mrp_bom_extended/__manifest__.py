# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    "name": "MRP BOM: Extended Product Attributes",
    'summary': "Web",
    'description': """
MRP BOM: Extended Product Attributes
====================================
- While creating MO from sales order consider the attribute values which dont create variants.
""",
    "author": "Odoo Inc",
    'website': "https://www.odoo.com",
    'category': 'Custom Development',
    'version': '0.1',
    'depends': ['sale', 'mrp'],
    'data': [
    ],
    'license': 'OEEL-1',
    'cloc_exclude': ['**/*'],
}