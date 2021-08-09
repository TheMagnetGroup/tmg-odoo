# -*- coding: utf-8 -*-
{
    'name': "TMG Product Extensions",

    'summary': """
        Extends the base product module for TMG""",

    'description': """
        This TMG module extends the product module to allow for attribute price extras based on quantity breaks
        * Jon W. Bergt 2020-06-11 - mrp_job added to 'depends' list to ensure job_id is available in tmg_product load
        * Jona Temple 2020-11-10 - Added models and code to support the ability to verify and create a standard product xml. Also
            added code to import ASI/SAGE categories and to export product data to SAGE.
        * Jonas Temple 2021-01-14 - Added price grid inquiry
        * Christian Dunn 2021-08-09 - Added Brands concept to Product Category
    """,

    'author': "The Magnet Group",
    'website': "http://www.themagnetgroup.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['product','sale','website_sale','mrp_job'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/price_grid_inquiry_wizard.xml',
        'views/tmg_product_views.xml',
        'views/tmg_product_category_views',
        'data/cron.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
