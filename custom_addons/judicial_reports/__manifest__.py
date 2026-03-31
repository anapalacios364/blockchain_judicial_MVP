{
    'name': 'Judicial Reports',
    'version': '19.0.1.0.0',
    'summary': 'Reportes PDF del expediente judicial y auditoría básica',
    'license': 'LGPL-3',
    'depends': ['judicial_base', 'web'],
    'data': ['reports/judicial_case_report.xml', 'views/report_menu.xml'],
    'application': True,
    'installable': True,
}
