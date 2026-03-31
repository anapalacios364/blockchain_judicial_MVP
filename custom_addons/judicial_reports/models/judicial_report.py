from odoo import models


class JudicialCaseReport(models.AbstractModel):
    _name = "report.judicial_reports.case_report_template"
    _description = "Reporte de expediente judicial"

    def _get_report_values(self, docids, data=None):
        docs = self.env["judicial.case"].browse(docids)
        return {"docs": docs}
