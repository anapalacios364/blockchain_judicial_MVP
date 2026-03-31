from odoo import http
from odoo.http import request


class JudicialPortal(http.Controller):
    @http.route(["/my/judicial/cases"], type="http", auth="user", website=True)
    def portal_cases(self, **kw):
        partner = request.env.user.partner_id
        cases = request.env["judicial.case"].sudo().search([("partner_id", "=", partner.id)])
        return request.render(
            "judicial_portal.portal_my_cases",
            {
                "page_name": "judicial_cases",
                "cases": cases,
            },
        )
