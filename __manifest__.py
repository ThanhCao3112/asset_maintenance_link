{
    'name': 'Asset & Maintenance Link',
    'version': '1.0',
    'summary': 'Bridge module to link accounting assets and maintenance equipment',
    'author': 'Your Company',
    'website': 'https://star-global.com',
    'category': 'Maintenance',
    'depends': ['maintenance', 'om_account_asset'],
    'data': [
        'views/account_asset_views.xml',
        'views/maintenance_equipment_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
