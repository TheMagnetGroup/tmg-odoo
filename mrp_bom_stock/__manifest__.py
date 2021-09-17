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
    'depends': ['mrp', 'sale_stock', 'purchase', 'tmg_available_to_sell'],
    'data': [
        'security/ir.model.access.csv',
        'views/purchase_views.xml',
        'views/mrp_bom_views.xml',
        'report/report_stock_kit_views.xml',
        'views/product_views.xml',
        'views/stock_location_views.xml'
    ],
    'post_init_hook': '_update_locations',
    'license': 'OEEL-1',
    'cloc_exclude': ['**/*'],
}
