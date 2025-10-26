{
    'name': 'SmartHive Client',
    'version': '17.0.1.0.0',
    'category': 'Administration',
    'summary': 'SmartHive client addon for remote management and payment monitoring',
    'description': """
SmartHive Client
================

This addon provides access control and warning management for your Odoo 17 CE instance.

Key Features:
* Local admin mode for standalone operation
* Remote management via SmartHive server (optional)
* Access control and blocking capabilities
* Payment status warning banners
* Super admin controls for local management
* Automatic status reporting to server (when configured)
* Secure API communication
* Heartbeat monitoring

Works standalone in local admin mode or with SmartHive server addon on Odoo 18 EE.
    """,
    'author': 'SmartHive',
    'website': 'https://www.smarthive.com',
    'license': 'LGPL-3',
    'depends': ['base', 'web', 'mail', 'crm'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/default_admin_assignment.xml',
        'data/ir_cron_data.xml',
        'views/client_config_views.xml',
        'views/warning_wizard_views.xml',
        'views/crm_warning_wizard_views.xml',
        'views/crm_integration_views.xml',
        'views/warning_banner_views.xml',
        'views/menu_views.xml',
        'templates/warning_banner_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'smarthive_client/static/src/js/warning_banner.js',
            'smarthive_client/static/src/js/crm_warning_service.js',
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