# -*- coding: utf-8 -*-
{
    'name': "tmg_attachment_types",

    'summary': """
        Adds an "Attachments" tab and includes the "Attachment Category"
        """,

    'description': """
    Adds many2many field "Attachment Category" that indicates the nature of the attachment. This field is not required.
    Adds an "Attachments" tab to the sales order form view and includes the "Attachment Category".  
    Creating/editing/deleting attachment categories restricted to Administrative Settings group.
    """,

    'author': "The Magnet Group",
    'website': "http://www.themagnetgroup.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'security/tmg_attachment_types_security.xml',
        'views/tmg_attachment_types_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
