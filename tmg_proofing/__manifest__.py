# -*- coding: utf-8 -*-
{
    'name': "tmg_proofing",

    'summary': """
        Creates the concept of sending customer's proofs in Odoo """,

    'description': """
        Proofs can be sent on the Sale Line to the customer to review to begin the proofing process
    """,

    'author': "The Magnet Group",
    'website': "http://www.themagnetgroup.com",


    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['tmg_sale', 'mrp_job', 'tmg_sale_stock', 'pr1_s3'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/proofing_wizard.xml',
        'views/views.xml',
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}