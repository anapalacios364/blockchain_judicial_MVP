from odoo import models


class JudicialCase(models.Model):
    _inherit = "judicial.case"

    def action_view_blockchain_logs(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Bitácora blockchain",
            "res_model": "judicial.blockchain.log",
            "view_mode": "list,form",
            "domain": [("case_id", "=", self.id)],
        }
