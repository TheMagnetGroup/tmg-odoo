# -*- coding: utf-8 -*-
{
    'name': "TMG Acounting Extensions",

    'summary': """
        Extends the Odoo accounting module with TMG specific extensions
        """,

    'description': """
        CJT - 2020/04/03 - Added remit_to_id to res.company.  Modified the invoice report to use the remit
                            to address instead of the company's address.   Added TMG specific layout changes to 
                            the invoice.
    """,

    'author': "The Magnet Group",
    'website': "http://www.themagnetgroup.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account_accountant','l10n_us_check_printing'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/tmg_report_invoice.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}