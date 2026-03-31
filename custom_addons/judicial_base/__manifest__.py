{
    'name': 'Judicial Base',
    'version': '19.0.1.0.0',
    'summary': 'Núcleo del dominio judicial para expedientes, partes y evidencias',
    'license': 'LGPL-3',
    'depends': ['base', 'mail', 'portal', 'web'],
    'data': ['security/judicial_groups.xml', 'security/ir.model.access.csv', 'views/judicial_case_views.xml', 'views/judicial_document_views.xml', 'views/judicial_dashboard_views.xml', 'views/judicial_menus.xml'],
    'application': True,
    'installable': True,
}
