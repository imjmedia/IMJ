# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Budget Purchase IMJ',
    'version' : '1.1',
    'summary': 'IMJ',
    'sequence': 1,
    'description': """
            Module add validation of budget in purchase""",
    'category': 'Account',
    'website': 'https://www.odoo.com/',
    'depends' : ['account','account_budget','purchase'],
    'data': ['security/imj_security.xml',
        'views/account_view.xml',
        'views/purchase_view.xml',
        'wizard/wiz_cam.xml',
            
            ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'auto_install': False,
}
