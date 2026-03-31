import json

from odoo import models
from odoo.exceptions import UserError

try:
    from web3 import Web3
except Exception:  # pragma: no cover
    Web3 = None


class BlockchainService(models.AbstractModel):
    _name = "judicial.blockchain.service"
    _description = "Servicio de integración blockchain judicial"

    def _params(self):
        icp = self.env["ir.config_parameter"].sudo()
        return {
            "rpc": icp.get_param("judicial.polygon_rpc_url") or self.env["ir.config_parameter"].sudo().get_param("judicial_polygon_rpc_url"),
            "chain_id": int(icp.get_param("judicial.chain_id") or 80002),
            "private_key": icp.get_param("judicial.private_key"),
            "contract_address": icp.get_param("judicial.contract_address"),
            "contract_abi": icp.get_param("judicial.contract_abi"),
        }

    def _get_web3(self):
        if Web3 is None:
            raise UserError("La dependencia web3 no está instalada.")
        rpc = self._params()["rpc"]
        if not rpc:
            raise UserError("Configura el RPC de Polygon en Ajustes.")
        web3 = Web3(Web3.HTTPProvider(rpc))
        if not web3.is_connected():
            raise UserError("No fue posible conectar con el RPC configurado.")
        return web3

    def store_case_hash(self, case, hash_hex):
        params = self._params()
        if not params["private_key"] or not params["contract_address"] or not params["contract_abi"]:
            raise UserError("Configura private key, contract address y ABI en Ajustes.")

        web3 = self._get_web3()
        abi = json.loads(params["contract_abi"])
        account = web3.eth.account.from_key(params["private_key"])
        contract = web3.eth.contract(
            address=web3.to_checksum_address(params["contract_address"]),
            abi=abi,
        )

        case_id_bytes = web3.keccak(text=case.name)
        document_hash_bytes = web3.to_bytes(hexstr=hash_hex)
        nonce = web3.eth.get_transaction_count(account.address)

        tx = contract.functions.anchorHash(case_id_bytes, document_hash_bytes).build_transaction(
            {
                "from": account.address,
                "nonce": nonce,
                "chainId": params["chain_id"],
                "gas": 250000,
                "gasPrice": web3.eth.gas_price,
            }
        )

        signed_tx = web3.eth.account.sign_transaction(tx, params["private_key"])
        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        tx_hash_hex = web3.to_hex(tx_hash)

        log = self.env["judicial.blockchain.log"].create(
            {
                "case_id": case.id,
                "document_id": case.active_document_id.id,
                "tx_hash": tx_hash_hex,
                "case_id_hex": case_id_bytes.hex(),
                "document_hash": hash_hex,
                "wallet_address": account.address,
                "response_payload": json.dumps(
                    {
                        "rpc": params["rpc"],
                        "contract": params["contract_address"],
                        "nonce": nonce,
                    }
                ),
            }
        )
        if case.active_document_id:
            case.active_document_id.blockchain_tx_hash = tx_hash_hex

        return {
            "tx_hash": tx_hash_hex,
            "case_id": case_id_bytes.hex(),
            "wallet": account.address,
            "log_id": log.id,
        }
