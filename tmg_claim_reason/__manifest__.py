# -*- coding: utf-8 -*-
{
    'name': "TMG Claim Reason",

    'summary': """
        Adds claim reason to the credit note.""",

    'description': """
        Adds a claim reason to the credit note that can notify a certain group of it's activity.
    """,

    'author': "The Magnet Group",
    'website': "http://www.themagnetgroup.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Account',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/tmg_account_invoice_view.xml',
        'wizard/credit_note_claim.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
