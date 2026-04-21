/** @odoo-module **/

import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";
import {Component, onWillStart, useState} from "@odoo/owl";

class JudicialDashboard extends Component {
    static template = "judicial_base.JudicialDashboardTemplate";
    static props = ["*"];

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");

        this.openCases = this.openCases.bind(this);
        this.openDocuments = this.openDocuments.bind(this);
        this.openBitacora = this.openBitacora.bind(this);
        this.refresh = this.refresh.bind(this);

        this.state = useState({
            loading: true,
            total_cases: 0,
            anchored_cases: 0,
            open_cases: 0,
            closed_cases: 0,
            draft_cases: 0,
            in_process_cases: 0,
            cases_this_month: 0,
            total_documents: 0,
            official_evidence_count: 0,
            documents_with_hash: 0,
            total_anchors: 0,
            confirmed_anchors: 0,
            failed_anchors: 0,
            pending_anchors: 0,
            anchor_success_rate: 0,
            anchors_today: 0,
            anchors_this_week: 0,
        });

        onWillStart(async () => {
            await this._loadData();
        });
    }

    async _loadData() {
        try {
            const data = await this.orm.call(
                "judicial.dashboard",
                "get_dashboard_data",
                []
            );
            Object.assign(this.state, data);
        } catch (e) {
            console.error("Error cargando dashboard judicial:", e);
        } finally {
            this.state.loading = false;
        }
    }

    _pct(value) {
        const total = this.state.total_cases;
        if (!total) return 0;
        return Math.round((value / total) * 100);
    }

    get pctDraft() {
        return this._pct(this.state.draft_cases);
    }

    get pctProcess() {
        return this._pct(this.state.in_process_cases);
    }

    get pctAnchored() {
        return this._pct(this.state.anchored_cases);
    }

    get pctClosed() {
        return this._pct(this.state.closed_cases);
    }

    openCases(state) {
        const domain = state ? [["state", "=", state]] : [];
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Expedientes",
            res_model: "judicial.case",
            views: [[false, "list"], [false, "form"]],
            domain: domain,
        });
    }

    openDocuments() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Documentos",
            res_model: "judicial.document",
            views: [[false, "list"], [false, "form"]],
            domain: [],
        });
    }

    openBitacora() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Bitácora blockchain",
            res_model: "judicial.blockchain.log",
            views: [[false, "list"], [false, "form"]],
            domain: [],
        });
    }

    async refresh() {
        this.state.loading = true;
        await this._loadData();
    }
}

registry.category("actions").add("judicial_dashboard_client_action", JudicialDashboard);