from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, Gauge, generate_latest

from odoo import http
from odoo.http import request


class JudicialMetricsController(http.Controller):
    @http.route("/judicial/metrics", type="http", auth="none", csrf=False)
    def judicial_metrics(self, **kwargs):
        registry = CollectorRegistry()
        total_cases = Gauge("judicial_total_cases", "Total de expedientes", registry=registry)
        anchored_cases = Gauge("judicial_anchored_cases", "Expedientes anclados", registry=registry)
        total_logs = Gauge("judicial_blockchain_logs_total", "Transacciones blockchain registradas", registry=registry)

        env = request.env
        total_cases.set(env["judicial.case"].sudo().search_count([]))
        anchored_cases.set(env["judicial.case"].sudo().search_count([("state", "=", "anchored")]))
        total_logs.set(env["judicial.blockchain.log"].sudo().search_count([]))

        payload = generate_latest(registry)
        headers = [("Content-Type", CONTENT_TYPE_LATEST)]
        return request.make_response(payload, headers=headers)
