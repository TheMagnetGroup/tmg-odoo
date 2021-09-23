# -*- coding: utf-8 -*-
{
        "name": "TMG Sales Order Hold",
    'summary': "Creates a new sale.hold module for the sale order.",
    'description': """
    
Add sales holds to orders that can block production or delivery. Also implements a credit check on the sales order to place orders on credit hold under certain conditions

    * Christian Dunn – 1/15/2020 – Changed what shipping labels used to get ship from company name
    * Christian Dunn – 4/02/2020 – Added picking logic to manufacturing order's picking. 
    * Christian Dunn - 9/29/2020 - Changed to only check holds on line items <> service.
    * Christian Dunn - 2/22/2021 - Added confirmation hold and logic.
    * Christian Dunn - 9/23/2021 - Fixed bug when update deliveries was executed.
    
""",
    "author": "The Magnet Group",
    'website': "http://www.themagnetgroup.com",
    'category': 'Sale',
    'version': '0.1',
    # any module necessary for this one to work correctly
    'depends': ['sale_management', 'sale_stock', 'mrp_job', 'tmg_mrp', 'tmg_external_api'],

    # always loaded
    'data': [
        'views/sale_hold_views.xml',
        'security/ir.model.access.csv',
        'views/manufacturing_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}