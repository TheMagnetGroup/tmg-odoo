# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    "name": "Manufacturing JOB: Multiple MO processing",
    'summary': "Web",
    'description': """
Manufacturing JOB: Muliple MO processing

    * Christian Dunn - 2020/02/07 -   Added picking location to sale report.
    * Christian Dunn - 2020/04/23 -   Limited visibility of the printed button on Sale Order.
    * Christian Dunn - 2021/03/11 -   Changes to MRP Report
    * Christian Dunn - 2021/05/25 -   Added unallocated notice to report
    * Christian Dunn - 2021/05/25 -   Added attention_to to castelli report
""",
    "author": "Odoo Inc",
    'website': "https://www.odoo.com",
    'category': 'Manufacturing',
    'version': '0.2',
    'depends': ['mrp', 'sale', 'mrp_bom_extended'],
    'data': [
        'security/ir.model.access.csv',
        'data/server_action.xml',
        'views/mrp_job_views.xml',
        'views/sale_order_views.xml',
        'views/mrp_production_views.xml',
        'views/stock_picking_views.xml' ,
        'report/castelli_report_mrporder.xml',
        'report/castelli_mrp_report.xml'
    ],
    'license': 'OEEL-1',
    'application': True
}
