{
    "name": """S3 Attachment Storage - Amazon S3, Owncloud, any S3""",
    "summary": """Store your attachments on any S3 storage connector. Amazon, OwnCloud, etc.""",
    "description":"""This module allows you to store attachments on any S3 storage connector. Amazon, Owncloud etc.
    This module supports multiple S3 Buckets. It also allows filtering to only upload specific mime types per model.
    The module can also be used to upload existing attachments into the S3 cloud.
    The module preserves file names unlike some other S3 connectors.
    This module also deletes attachments from S3 when they are removed from Odoo.
    Amazon, S3, Amazon S3, Owncloud, Own Cloud. """,
    "category": "Tools",
    "version": "1.0.0",
    "application": True,

    "author": "PR1",
    "website": "https://pr1.xyz",
    "license": "AGPL-3",
    "price": 150.00,
    "currency": "EUR",
    'images': ['static/description/banner.jpg'],
    "depends": [
        'base_setup','document'
    ],
    "external_dependencies": {"python": ['boto3']},
    "data": [
        "security/security.xml",
        'security/ir.model.access.csv',
        "views/s3_connection_view.xml",
        "views/bucket_filter_view.xml",
        # "views/attachment_view.xml",
    ],
    "auto_install": False,
    "installable": True,
}
