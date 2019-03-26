# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    "name": "Mrp Bom Stock: Product Stock Based on BOM",
    'summary': "Web",
    'description': """
Mrp Bom Stock: Product Stock Based on BOM
=========================================
- Calculation of all inventroy values on product/product template based on the bom for the related product.
""",
    "author": "Odoo Inc",
    'website': "https://www.odoo.com",
    'category': 'Custom Development',
    'version': '0.1',
    'depends': ['mrp', 'sale_stock'],
    'data': [
        'views/mrp_bom_views.xml'
    ],
    'license': 'OEEL-1',
}