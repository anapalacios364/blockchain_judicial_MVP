import time
import threading

from odoo import http
from odoo.http import request

_lock = threading.Lock()

_in_flight_requests = 0        # Solicitudes de anclaje activas en este momento
_rpc_errors_total = 0          # Errores acumulados de conexión al nodo EVM
_rpc_timeouts_total = 0        # Timeouts acumulados del RPC
_anchor_retry_total = 0        # Reintentos de anclaje acumulados
_last_anchor_duration_ms = 0.0 # Duración del último anclaje exitoso (ms)
_peak_concurrent = 0           # Máximo de solicitudes concurrentes registrado


def record_anchor_start():
    """Llamar al inicio de un intento de anclaje."""
    global _in_flight_requests, _peak_concurrent
    with _lock:
        _in_flight_requests += 1
        if _in_flight_requests > _peak_concurrent:
            _peak_concurrent = _in_flight_requests


def record_anchor_end(duration_ms: float):
    """Llamar al finalizar un anclaje (exitoso o no)."""
    global _in_flight_requests, _last_anchor_duration_ms
    with _lock:
        _in_flight_requests = max(0, _in_flight_requests - 1)
        _last_anchor_duration_ms = duration_ms


def record_rpc_error():
    global _rpc_errors_total
    with _lock:
        _rpc_errors_total += 1


def record_rpc_timeout():
    global _rpc_timeouts_total
    with _lock:
        _rpc_timeouts_total += 1


def record_anchor_retry():
    global _anchor_retry_total
    with _lock:
        _anchor_retry_total += 1


def _safe_int(val, default=0):
    try:
        return int(val)
    except Exception:
        return default


def _prom_line(name, value, help_text="", metric_type="gauge", labels=None):
    """Genera las líneas de una métrica en formato Prometheus text exposition."""
    lines = []
    if help_text:
        lines.append(f"# HELP {name} {help_text}")
    if metric_type:
        lines.append(f"# TYPE {name} {metric_type}")
    label_str = ""
    if labels:
        label_parts = ",".join(f'{k}="{v}"' for k, v in labels.items())
        label_str = f"{{{label_parts}}}"
    lines.append(f"{name}{label_str} {value}")
    return lines


def _collect_metrics(env):
    """
    Recopila todas las métricas desde la base de datos y los contadores en memoria.
    Devuelve una lista de líneas en formato Prometheus.
    """
    lines = []
    now = time.time()

    Log = env["judicial.blockchain.log"].sudo()
    Case = env["judicial.case"].sudo()

    all_logs = Log.search([])
    total_anchors = len(all_logs)

    # Anclajes con tx_hash (exitosos)
    successful_anchors = len(all_logs.filtered(lambda l: bool(l.tx_hash)))

    # Anclajes fallidos (registrados pero sin tx_hash)
    failed_anchors = total_anchors - successful_anchors

    # Tasa de éxito (0.0 – 1.0)
    anchor_success_rate = (
        round(successful_anchors / total_anchors, 4) if total_anchors > 0 else 0.0
    )

    # Expedientes con estado "anchored" (trazabilidad on-chain confirmada)
    anchored_cases = Case.search_count([("state", "=", "anchored")])
    total_cases = Case.search_count([])

    # Verificación de integridad: expedientes con hash almacenado en Odoo
    cases_with_hash = Case.search_count(
        [("active_document_hash", "!=", False), ("active_document_hash", "!=", "")]
    )

    # Casos con referencia blockchain completa (tx + caseId + wallet + fecha)
    cases_fully_traced = Case.search_count(
        [
            ("blockchain_tx_hash", "!=", False),
            ("blockchain_case_id", "!=", False),
            ("blockchain_anchor_address", "!=", False),
            ("blockchain_anchor_at", "!=", False),
        ]
    )

    # Tasa de trazabilidad completa
    traceability_rate = (
        round(cases_fully_traced / total_cases, 4) if total_cases > 0 else 0.0
    )

    lines += _prom_line(
        "judicial_anchor_total",
        total_anchors,
        help_text="Total de intentos de anclaje registrados",
        metric_type="counter",
    )
    lines += _prom_line(
        "judicial_anchor_success_total",
        successful_anchors,
        help_text="Anclajes completados con tx_hash confirmado",
        metric_type="counter",
    )
    lines += _prom_line(
        "judicial_anchor_failed_total",
        failed_anchors,
        help_text="Anclajes registrados sin tx_hash (fallidos)",
        metric_type="counter",
    )
    lines += _prom_line(
        "judicial_anchor_success_rate",
        anchor_success_rate,
        help_text="Tasa de éxito de anclajes (0.0 a 1.0)",
        metric_type="gauge",
    )
    lines += _prom_line(
        "judicial_cases_total",
        total_cases,
        help_text="Total de expedientes judiciales en el sistema",
        metric_type="gauge",
    )
    lines += _prom_line(
        "judicial_cases_anchored",
        anchored_cases,
        help_text="Expedientes con estado 'anchored' (trazabilidad on-chain confirmada)",
        metric_type="gauge",
    )
    lines += _prom_line(
        "judicial_cases_with_hash",
        cases_with_hash,
        help_text="Expedientes con hash de documento almacenado en Odoo",
        metric_type="gauge",
    )
    lines += _prom_line(
        "judicial_cases_fully_traced",
        cases_fully_traced,
        help_text="Expedientes con trazabilidad blockchain completa (tx+caseId+wallet+fecha)",
        metric_type="gauge",
    )
    lines += _prom_line(
        "judicial_traceability_rate",
        traceability_rate,
        help_text="Porcentaje de expedientes con trazabilidad completa (0.0 a 1.0)",
        metric_type="gauge",
    )

    # Distribución de estados de expedientes
    for state_val, state_label in [
        ("draft", "borrador"),
        ("in_process", "en_proceso"),
        ("anchored", "anclado"),
        ("closed", "cerrado"),
    ]:
        count = Case.search_count([("state", "=", state_val)])
        lines += _prom_line(
            "judicial_cases_by_state",
            count,
            help_text="Expedientes agrupados por estado",
            metric_type="gauge",
            labels={"state": state_val, "label": state_label},
        )

    lines.append("")

    import datetime
    one_hour_ago = datetime.datetime.now() - datetime.timedelta(hours=1)
    recent_anchors = Log.search_count(
        [("create_date", ">=", one_hour_ago.strftime("%Y-%m-%d %H:%M:%S"))]
    )

    # Anclajes en los últimos 10 minutos (carga inmediata)
    ten_min_ago = datetime.datetime.now() - datetime.timedelta(minutes=10)
    very_recent_anchors = Log.search_count(
        [("create_date", ">=", ten_min_ago.strftime("%Y-%m-%d %H:%M:%S"))]
    )

    # Throughput estimado (TPS = transacciones por segundo en ventana de 10 min)
    tps_10min = round(very_recent_anchors / 600, 6)  # 600 segundos = 10 min

    # Documentos judiciales en el sistema (volumen de datos)
    total_docs = _safe_int(
        env["judicial.document"].sudo().search_count([])
    )

    with _lock:
        in_flight = _in_flight_requests
        peak_conc = _peak_concurrent
        last_dur = _last_anchor_duration_ms

    lines += _prom_line(
        "judicial_anchor_requests_1h",
        recent_anchors,
        help_text="Anclajes realizados en la última hora",
        metric_type="gauge",
    )
    lines += _prom_line(
        "judicial_anchor_requests_10m",
        very_recent_anchors,
        help_text="Anclajes realizados en los últimos 10 minutos",
        metric_type="gauge",
    )
    lines += _prom_line(
        "judicial_anchor_tps_10m",
        tps_10min,
        help_text="Throughput estimado de anclajes (tx/segundo, ventana 10 min)",
        metric_type="gauge",
    )
    lines += _prom_line(
        "judicial_anchor_in_flight",
        in_flight,
        help_text="Solicitudes de anclaje activas en este momento (concurrencia actual)",
        metric_type="gauge",
    )
    lines += _prom_line(
        "judicial_anchor_peak_concurrent",
        peak_conc,
        help_text="Máximo de anclajes concurrentes registrado desde el arranque",
        metric_type="gauge",
    )
    lines += _prom_line(
        "judicial_anchor_last_duration_ms",
        last_dur,
        help_text="Duración del último anclaje completado en milisegundos",
        metric_type="gauge",
    )
    lines += _prom_line(
        "judicial_documents_total",
        total_docs,
        help_text="Total de documentos judiciales registrados en el sistema",
        metric_type="gauge",
    )
    lines.append("")


    with _lock:
        rpc_errors = _rpc_errors_total
        rpc_timeouts = _rpc_timeouts_total
        retries = _anchor_retry_total

    rpc_available = 0
    rpc_response_ms = 0.0
    try:
        icp = env["ir.config_parameter"].sudo()
        import os
        rpc_url = (
            icp.get_param("judicial.polygon_rpc_url")
            or os.getenv("JUDICIAL_EVM_RPC_URL")
            or os.getenv("JUDICIAL_POLYGON_RPC_URL")
        )
        if rpc_url:
            try:
                from web3 import Web3
                t_start = time.time()
                w3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={"timeout": 5}))
                connected = w3.is_connected()
                rpc_response_ms = round((time.time() - t_start) * 1000, 2)
                rpc_available = 1 if connected else 0
            except Exception:
                rpc_available = 0
    except Exception:
        rpc_available = 0

    anchor_error_rate = (
        round(failed_anchors / total_anchors, 4) if total_anchors > 0 else 0.0
    )

    lines += _prom_line(
        "judicial_rpc_available",
        rpc_available,
        help_text="Disponibilidad del nodo EVM/RPC (1=disponible, 0=no disponible)",
        metric_type="gauge",
    )
    lines += _prom_line(
        "judicial_rpc_response_ms",
        rpc_response_ms,
        help_text="Tiempo de respuesta del nodo RPC en milisegundos",
        metric_type="gauge",
    )
    lines += _prom_line(
        "judicial_rpc_errors_total",
        rpc_errors,
        help_text="Errores acumulados de conexión al nodo EVM desde el arranque",
        metric_type="counter",
    )
    lines += _prom_line(
        "judicial_rpc_timeouts_total",
        rpc_timeouts,
        help_text="Timeouts acumulados del RPC desde el arranque",
        metric_type="counter",
    )
    lines += _prom_line(
        "judicial_anchor_retry_total",
        retries,
        help_text="Reintentos de anclaje acumulados desde el arranque",
        metric_type="counter",
    )
    lines += _prom_line(
        "judicial_anchor_error_rate",
        anchor_error_rate,
        help_text="Tasa de error de anclajes (fallos / total, 0.0 a 1.0)",
        metric_type="gauge",
    )
    lines.append("")

    lines += _prom_line(
        "judicial_system_up",
        1,
        help_text="El módulo judicial está cargado y respondiendo (siempre 1 si llega aquí)",
        metric_type="gauge",
    )
    lines += _prom_line(
        "judicial_metrics_scrape_timestamp",
        round(now, 3),
        help_text="Timestamp Unix del último scrape de métricas",
        metric_type="gauge",
    )
    lines.append("")

    return lines


class JudicialMetricsController(http.Controller):

    @http.route("/judicial/metrics", type="http", auth="none", csrf=False)
    def metrics(self):
        """
        Endpoint Prometheus en formato text exposition 0.0.4.
        No requiere autenticación para que Prometheus pueda scrapearlo.
        """
        try:
            env = request.env(user=1)  # Ejecutar como superusuario interno
            lines = _collect_metrics(env)
            body = "\n".join(lines) + "\n"
            return request.make_response(
                body,
                headers=[
                    ("Content-Type", "text/plain; version=0.0.4; charset=utf-8"),
                    ("Cache-Control", "no-cache, no-store"),
                ],
            )
        except Exception as e:
            error_body = (
                "# HELP judicial_metrics_error Error al recopilar métricas\n"
                "# TYPE judicial_metrics_error gauge\n"
                f"judicial_metrics_error 1\n"
                f"# Error: {str(e)[:200]}\n"
            )
            return request.make_response(
                error_body,
                headers=[("Content-Type", "text/plain; version=0.0.4")],
            )