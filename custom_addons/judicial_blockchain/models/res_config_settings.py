from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    judicial_polygon_rpc_url = fields.Char(config_parameter="judicial.polygon_rpc_url")
    judicial_chain_id = fields.Integer(config_parameter="judicial.chain_id", default=80002)
    judicial_private_key = fields.Char(config_parameter="judicial.private_key")
    judicial_contract_address = fields.Char(config_parameter="judicial.contract_address")
    judicial_contract_abi = fields.Char(config_parameter="judicial_blockchain.judicial_contract_abi")