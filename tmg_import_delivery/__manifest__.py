# -*- coding: utf-8 -*-
{
    'name': "TMG Import Delivery",

    'summary': "Gives the user the ability to enter individual delivery orders and adds 3rd party fedex.",
    'description': """
    Adds the ability to add a third party shipper number for fedex deliveries and adds to tmg_sale_stock's ability to enter bulk shipments by adding the ability to enter individual shipments in wizard
    This also adds the ability to add 3rf party fedex  numbers. The bill my account setting and the dropdowns in picking and sales screens
    
          
        * Christian Dunn - 2020/02/07 -   Added attention to flag to the delivery order.
        * Christian Dunn - 2020/02/07 -   Fixed bug with fedex information not pulling over.
        * Jonas Temple   - 2020/06/08 -   Added attention to to the sale order report
        * Christian Dunn - 2020/09/29 -   Fixed bug causing the Bill_My_Account to have issues.
        * Christian Dunn - 2020/10/23 -   Added code to update delivery line at shipment.
        * Christian Dunn - 2021/06/11 -   Fixed order of default for UPS shipments.
        * Christian Dunn - 2021/06/23 -   Added field tracking for delivery methods.
    """,

    "author": "The Magnet Group",
    'website': "http://www.themagnetgroup.com",
    'category': 'Sale',
    'version': '12.2.2',
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list

    # any module necessary for this one to work correctly
    'depends': [ 'tmg_sale_stock','tmg_mrp','delivery_ups', 'delivery_fedex','sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/packaging_data.xml',
        'wizard/sale_order_line_delivery_entry_wizard.xml',
        'views/views.xml',
        'views/picking_view.xml',
        'views/packaging_view.xml',
        'wizard/compare_rates.xml',
        'views/fedex_provider_view.xml',
        'reports/tmg_sale.xml',


    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}