from odoo import api, fields, models


class JudicialDashboard(models.Model):
    _name = "judicial.dashboard"
    _description = "Dashboard Judicial MVP"

    name = fields.Char(default="Dashboard")
    total_cases = fields.Integer(compute="_compute_metrics")
    anchored_cases = fields.Integer(compute="_compute_metrics")
    open_cases = fields.Integer(compute="_compute_metrics")
    total_documents = fields.Integer(compute="_compute_metrics")

    @api.depends()
    def _compute_metrics(self):
        case_model = self.env["judicial.case"]
        doc_model = self.env["judicial.document"]
        for record in self:
            record.total_cases = case_model.search_count([])
            record.anchored_cases = case_model.search_count([("state", "=", "anchored")])
            record.open_cases = case_model.search_count([("state", "in", ["draft", "in_process"])])
            record.total_documents = doc_model.search_count([])
