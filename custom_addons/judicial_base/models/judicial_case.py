import hashlib

from odoo import api, fields, models
from odoo.exceptions import UserError


class JudicialCase(models.Model):
    _name = "judicial.case"
    _description = "Expediente Judicial"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    name = fields.Char(string="Código de expediente", required=True, tracking=True, copy=False, default="Nuevo")
    title = fields.Char(string="Título", required=True, tracking=True)
    description = fields.Text(string="Descripción")
    state = fields.Selection(
        [
            ("draft", "Borrador"),
            ("in_process", "En proceso"),
            ("anchored", "Anclado"),
            ("closed", "Cerrado"),
        ],
        string="Estado",
        default="draft",
        tracking=True,
    )
    partner_id = fields.Many2one("res.partner", string="Parte procesal principal", required=True, tracking=True)
    assigned_user_id = fields.Many2one("res.users", string="Responsable", default=lambda self: self.env.user)
    document_ids = fields.One2many("judicial.document", "case_id", string="Documentos")
    document_count = fields.Integer(string="Documentos", compute="_compute_document_count")
    active_document_id = fields.Many2one("judicial.document", string="Documento activo")
    active_document_hash = fields.Char(string="Hash del documento activo", readonly=True)
    blockchain_tx_hash = fields.Char(string="TX Hash", readonly=True, copy=False)
    blockchain_case_id = fields.Char(string="Case ID bytes32", readonly=True, copy=False)
    blockchain_anchor_at = fields.Datetime(string="Fecha de anclaje", readonly=True, copy=False)
    blockchain_anchor_address = fields.Char(string="Wallet ancla", readonly=True, copy=False)
    can_anchor = fields.Boolean(compute="_compute_can_anchor")

    @api.depends("document_ids")
    def _compute_document_count(self):
        for record in self:
            record.document_count = len(record.document_ids)

    @api.depends("active_document_id")
    def _compute_can_anchor(self):
        for record in self:
            record.can_anchor = bool(record.active_document_id)

    @api.model_create_multi
    def create(self, vals_list):
        sequence = self.env["ir.sequence"]
        for vals in vals_list:
            if vals.get("name", "Nuevo") == "Nuevo":
                vals["name"] = sequence.next_by_code("judicial.case") or "CASE-NEW"
        return super().create(vals_list)

    def action_set_active_document(self):
        for record in self:
            if not record.document_ids:
                raise UserError("El expediente no tiene documentos para activar.")
            record.active_document_id = record.document_ids[0].id

    def _generate_case_id_bytes32(self):
        self.ensure_one()
        from web3 import Web3

        return Web3.keccak(text=self.name).hex()

    def _generate_hash(self):
        self.ensure_one()
        if not self.active_document_id:
            raise UserError("Debes seleccionar un documento activo para generar el hash.")
        payload = self.active_document_id._hash_payload()
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def action_anchor_blockchain(self):
        for record in self:
            if not record.active_document_id:
                raise UserError("Selecciona un documento activo antes de anclar.")
            hash_hex = record._generate_hash()
            result = self.env["judicial.blockchain.service"].store_case_hash(record, hash_hex)
            record.write(
                {
                    "active_document_hash": hash_hex,
                    "blockchain_tx_hash": result.get("tx_hash"),
                    "blockchain_case_id": result.get("case_id"),
                    "blockchain_anchor_at": fields.Datetime.now(),
                    "blockchain_anchor_address": result.get("wallet"),
                    "state": "anchored",
                }
            )

    def action_view_documents(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Documentos",
            "res_model": "judicial.document",
            "view_mode": "list,form",
            "domain": [("case_id", "=", self.id)],
            "context": {"default_case_id": self.id},
        }

    def action_start(self):
        for record in self:
            if record.state != "draft":
                raise UserError("Solo un expediente en borrador puede iniciar.")
            record.state = "in_process"

    def action_close(self):
        for record in self:
            if record.state == "closed":
                continue
            if record.state == "draft":
                raise UserError("No puedes cerrar un expediente que no haya iniciado.")
            record.state = "closed"
