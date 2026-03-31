import base64
import hashlib

from odoo import fields, models
from odoo.exceptions import UserError


class JudicialDocument(models.Model):
    _name = "judicial.document"
    _description = "Documento Judicial"
    _order = "create_date desc"

    name = fields.Char(string="Nombre del documento", required=True)
    case_id = fields.Many2one("judicial.case", string="Expediente", required=True, ondelete="cascade")
    document_type = fields.Selection(
        [
            ("evidence", "Evidencia"),
            ("resolution", "Providencia"),
            ("filing", "Escrito"),
            ("other", "Otro"),
        ],
        string="Tipo",
        default="evidence",
        required=True,
    )
    attachment = fields.Binary(string="Archivo", attachment=True)
    filename = fields.Char(string="Nombre de archivo")
    notes = fields.Text(string="Observaciones")
    is_official_evidence = fields.Boolean(string="Evidencia oficial")
    sha256_hash = fields.Char(string="SHA-256", readonly=True)
    blockchain_tx_hash = fields.Char(string="TX Hash", readonly=True)

    def _hash_payload(self):
        self.ensure_one()
        if not self.attachment:
            raise UserError("El documento no tiene archivo adjunto.")
        binary = base64.b64decode(self.attachment)
        return f"{self.case_id.name}|{self.name}|{hashlib.sha256(binary).hexdigest()}"

    def action_compute_hash(self):
        for record in self:
            payload = record._hash_payload()
            record.sha256_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def action_mark_as_active(self):
        for record in self:
            record.case_id.active_document_id = record.id
            if not record.sha256_hash:
                record.action_compute_hash()
