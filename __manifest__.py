{
    'name': 'Custom PO Creation',
    "author": "Peter",
    'version': '17.0.1.0',
    'category': 'Sales',
    'summary': 'Control PO creation for Non-Moving-Products',
    'description': """
        Module that adds control on PO creation to prevent Non-Moving Product
    """,
    'data': [
        "views/custom_product_template.xml",
        "views/email_template.xml",
        "views/res_config_settings_views.xml",
    ],
    'depends': ['product', 'purchase'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
}
