{
    'name': 'SmartHive Client',
    'version': '17.0.1.0.0',
    'category': 'Administration',
    'summary': 'SmartHive client addon for remote management and payment monitoring',
    'description': """
SmartHive Client
================

This addon allows your Odoo 17 CE instance to be managed remotely by a SmartHive server.

Key Features:
* Remote access control and blocking
* Payment status warning banners
* Automatic status reporting to server
* Secure API communication
* Heartbeat monitoring

This addon works in conjunction with the SmartHive server addon on Odoo 18 EE.
    """,
    'author': 'SmartHive',
    'website': 'https://www.smarthive.com',
    'license': 'LGPL-3',
    'depends': ['base', 'web', 'mail'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_cron_data.xml',
        'views/client_config_views.xml',
        'views/warning_banner_views.xml',
        'views/menu_views.xml',
        'templates/warning_banner_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'smarthive_client/static/src/js/warning_banner.js',
            'smarthive_client/static/src/css/warning_banner.css',
        ],
        'web.assets_frontend': [
            'smarthive_client/static/src/css/warning_banner.css',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}