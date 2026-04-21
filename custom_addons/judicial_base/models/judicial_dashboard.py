from odoo import api, fields, models


class JudicialDashboard(models.TransientModel):
    _name = "judicial.dashboard"
    _description = "Dashboard Judicial MVP"

    name = fields.Char(default="Dashboard")

    total_cases = fields.Integer(string="Total expedientes")
    anchored_cases = fields.Integer(string="Anclados on-chain")
    open_cases = fields.Integer(string="Expedientes abiertos")
    closed_cases = fields.Integer(string="Cerrados")
    draft_cases = fields.Integer(string="Borrador")
    in_process_cases = fields.Integer(string="En proceso")
    cases_this_month = fields.Integer(string="Este mes")

    total_documents = fields.Integer(string="Total documentos")
    official_evidence_count = fields.Integer(string="Evidencias oficiales")
    documents_with_hash = fields.Integer(string="Con hash SHA-256")

    total_anchors = fields.Integer(string="Total anclajes")
    confirmed_anchors = fields.Integer(string="Confirmados")
    failed_anchors = fields.Integer(string="Fallidos")
    pending_anchors = fields.Integer(string="Pendientes")
    anchor_success_rate = fields.Float(string="Tasa de éxito", digits=(5, 1))
    anchors_today = fields.Integer(string="Hoy")
    anchors_this_week = fields.Integer(string="Esta semana")

    @api.model
    def get_dashboard_data(self):
        """Devuelve métricas calculadas en tiempo real."""
        from datetime import timedelta

        Case = self.env["judicial.case"]
        Doc = self.env["judicial.document"]
        LogModel = self.env.get("judicial.blockchain.log")

        today = fields.Date.today()
        week_start = today - timedelta(days=today.weekday())
        month_start = today.replace(day=1)

        total_cases = Case.search_count([])
        anchored_cases = Case.search_count([("state", "=", "anchored")])
        closed_cases = Case.search_count([("state", "=", "closed")])
        draft_cases = Case.search_count([("state", "=", "draft")])
        in_process_cases = Case.search_count([("state", "=", "in_process")])
        cases_this_month = Case.search_count([
            ("create_date", ">=", fields.Datetime.to_datetime(month_start))
        ])

        total_documents = Doc.search_count([])
        official_evidence_count = Doc.search_count([("is_official_evidence", "=", True)])
        documents_with_hash = Doc.search_count([
            ("sha256_hash", "!=", False), ("sha256_hash", "!=", "")
        ])

        total_anchors = confirmed = failed = pending = anchors_today = anchors_week = 0
        success_rate = 0.0

        if LogModel is not None:
            total_anchors = LogModel.search_count([])
            confirmed = LogModel.search_count([("status", "=", "confirmed")])
            failed = LogModel.search_count([("status", "=", "failed")])
            pending = LogModel.search_count([("status", "=", "pending")])
            anchors_today = LogModel.search_count([
                ("create_date", ">=", fields.Datetime.to_datetime(today))
            ])
            anchors_week = LogModel.search_count([
                ("create_date", ">=", fields.Datetime.to_datetime(week_start))
            ])
            success_rate = round(confirmed * 100.0 / total_anchors, 1) if total_anchors > 0 else 0.0

        return {
            "total_cases": total_cases,
            "anchored_cases": anchored_cases,
            "open_cases": draft_cases + in_process_cases,
            "closed_cases": closed_cases,
            "draft_cases": draft_cases,
            "in_process_cases": in_process_cases,
            "cases_this_month": cases_this_month,
            "total_documents": total_documents,
            "official_evidence_count": official_evidence_count,
            "documents_with_hash": documents_with_hash,
            "total_anchors": total_anchors,
            "confirmed_anchors": confirmed,
            "failed_anchors": failed,
            "pending_anchors": pending,
            "anchor_success_rate": success_rate,
            "anchors_today": anchors_today,
            "anchors_this_week": anchors_week,
        }