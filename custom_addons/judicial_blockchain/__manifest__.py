{
    'name': 'Judicial Blockchain',
    'version': '19.0.1.0.0',
    'summary': 'Integración Polygon/EVM para anclaje de hashes judiciales',
    'license': 'LGPL-3',
    'depends': ['base', 'judicial_base'],
    'data': ['security/ir.model.access.csv', 'views/res_config_settings_views.xml', 'views/judicial_blockchain_log_views.xml', 'views/judicial_case_inherit_views.xml'],
    'application': True,
    'installable': True,
}
