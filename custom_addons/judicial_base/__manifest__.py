{
    'name': 'Judicial Base',
    'version': '19.0.2.0.0',
    'summary': 'Núcleo del dominio judicial para expedientes, partes y evidencias',
    'license': 'LGPL-3',
    'depends': ['base', 'mail', 'portal', 'web'],
    'data': [
        'security/judicial_groups.xml',
        'security/ir.model.access.csv',
        'views/judicial_case_views.xml',
        'views/judicial_document_views.xml',
        'views/judicial_dashboard_views.xml',
        'views/judicial_menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'judicial_base/static/src/css/dashboard.css',
            'judicial_base/static/src/xml/dashboard.xml',
            'judicial_base/static/src/js/dashboard.js',
        ],
    },
    'application': True,
    'installable': True,
}