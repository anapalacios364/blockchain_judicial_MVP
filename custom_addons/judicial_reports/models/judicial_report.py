from odoo import models


class JudicialCaseReport(models.AbstractModel):
    _name = "report.judicial_reports.case_report_template"
    _description = "Reporte de expediente judicial"

    def _get_report_values(self, docids, data=None):
        docs = self.env["judicial.case"].browse(docids)
        return {"docs": docs}


class JudicialEvidenceReport(models.AbstractModel):
    _name = "report.judicial_reports.evidence_report_template"
    _description = "Reporte de evidencias marcadas"

    def _get_report_values(self, docids, data=None):
        docs = self.env["judicial.case"].browse(docids)
        # Construir lista de casos con solo sus documentos marcados como evidencia oficial
        evidence_data = []
        for case in docs:
            evidence_docs = case.document_ids.filtered(lambda d: d.is_official_evidence)
            evidence_data.append({
                "case": case,
                "evidence_docs": evidence_docs,
            })
        return {
            "docs": docs,
            "evidence_data": evidence_data,
        }
