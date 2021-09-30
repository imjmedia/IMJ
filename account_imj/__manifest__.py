# -*- coding: utf-8 -*-

{
    'name' : 'Contabilidad IJM',
    'shortdesc': 'Contabilidad IJM',
    'version' : '13.1.0',
    'summary': 'Account modifications specifically for IMJ',
    'description': """
        All small modifications to the account module will be placed inside this module.
         """,
    'category': 'Account',
    'author': 'InuX',
    'website': 'https://www.odoo.com/',
    'depends' : ['account','purchase','l10n_mx_edi'],
    'data': ['views/account_view.xml',
            'views/purchase_order_view.xml',
            'views/res_partner_view.xml',
            ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'auto_install': False,
}
