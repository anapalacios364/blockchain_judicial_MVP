from odoo import fields, models


class JudicialBlockchainLog(models.Model):
    _name = "judicial.blockchain.log"
    _description = "Bitácora Blockchain"
    _order = "create_date desc"

    case_id = fields.Many2one("judicial.case", string="Expediente", required=True, ondelete="cascade")
    document_id = fields.Many2one("judicial.document", string="Documento")
    tx_hash = fields.Char(string="Transacción", required=True)
    case_id_hex = fields.Char(string="Case ID")
    document_hash = fields.Char(string="Hash documento")
    wallet_address = fields.Char(string="Wallet")
    network_name = fields.Char(string="Red", default="Polygon")
    status = fields.Selection(
        [("pending", "Pendiente"), ("confirmed", "Confirmada"), ("failed", "Fallida")],
        default="confirmed",
        required=True,
    )
    response_payload = fields.Text(string="Payload")
