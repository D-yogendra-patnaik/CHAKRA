// Chakra AI Safety Platform — app.js
(function () {
    "use strict";
    const API = "/v1";

    // --- Pillar Tab Navigation ---
    const tabs = document.querySelectorAll(".pillar-tab");
    const sections = document.querySelectorAll(".pillar-section");

    tabs.forEach(tab => {
        tab.addEventListener("click", () => {
            tabs.forEach(t => t.classList.remove("active"));
            sections.forEach(s => s.classList.add("hidden"));
            tab.classList.add("active");
            document.getElementById("pillar-" + tab.dataset.pillar).classList.remove("hidden");

            // Refresh data when switching tabs
            if (tab.dataset.pillar === "scorecard") refreshScorecard();
            if (tab.dataset.pillar === "audit") refreshAudit();
        });
    });

    // Clock
    const clockEl = document.getElementById("clock");
    function tick() { clockEl.textContent = new Date().toLocaleTimeString(); }
    setInterval(tick, 1000);
    tick();

    // ============================================================
    // PILLAR 1: AI Red Team Simulator
    // ============================================================
    const btnRedteam = document.getElementById("btn-redteam");
    const rtResults = document.getElementById("rt-results");
    const rtResultsEmpty = document.getElementById("rt-results-empty");

    btnRedteam.addEventListener("click", async () => {
        const cats = [...document.querySelectorAll("#rt-categories input:checked")].map(cb => cb.value);
        if (cats.length === 0) { alert("Select at least one category."); return; }

        btnRedteam.disabled = true;
        btnRedteam.textContent = "⏳ Running...";

        try {
            const res = await fetch(`${API}/redteam/run`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    suite_name: "dashboard_suite",
                    tenant_id: document.getElementById("rt-tenant").value,
                    categories: cats
                })
            });
            const data = await res.json();
            showRedTeamResults(data);
        } catch (err) { alert("Error: " + err.message); }
        finally {
            btnRedteam.disabled = false;
            btnRedteam.textContent = "🚀 Launch Red Team Suite";
        }
    });

    function showRedTeamResults(data) {
        rtResultsEmpty.classList.add("hidden");
        rtResults.classList.remove("hidden");
        const s = data.results_summary;

        // KPI row
        document.getElementById("rt-kpi-row").innerHTML = `
            <div class="rt-stat"><span class="rt-num" style="color:var(--red)">${s.blocked}</span><span class="rt-label">Blocked</span></div>
            <div class="rt-stat"><span class="rt-num" style="color:var(--amber)">${s.warned}</span><span class="rt-label">Warned</span></div>
            <div class="rt-stat"><span class="rt-num" style="color:var(--green)">${s.allowed}</span><span class="rt-label">Allowed</span></div>
            <div class="rt-stat"><span class="rt-num" style="color:var(--cyan)">${s.sanitized || 0}</span><span class="rt-label">Sanitized</span></div>
        `;

        // Detection rate
        const detEl = document.getElementById("rt-detection");
        detEl.textContent = `Detection Rate: ${s.detection_rate}%`;
        detEl.style.background = s.detection_rate > 70 ? "linear-gradient(135deg,#059669,#34d399)" :
                                 s.detection_rate > 40 ? "linear-gradient(135deg,#d97706,#fbbf24)" :
                                 "linear-gradient(135deg,#dc2626,#f87171)";
        detEl.style.color = "#fff";

        // Category breakdown
        const catBreakdown = s.category_breakdown || {};
        document.getElementById("rt-category-breakdown").innerHTML = Object.entries(catBreakdown).map(([cat, stats]) => `
            <div class="rt-category-row">
                <span style="font-weight:600;text-transform:capitalize">${cat.replace(/_/g, ' ')}</span>
                <span>
                    <span style="color:var(--red)">${stats.blocked}B</span> ·
                    <span style="color:var(--amber)">${stats.warned}W</span> ·
                    <span style="color:var(--green)">${stats.allowed}A</span> ·
                    <span style="color:var(--cyan)">${stats.sanitized || 0}S</span>
                    / ${stats.total}
                </span>
            </div>
        `).join("");

        // Per-prompt list
        document.getElementById("rt-prompt-list").innerHTML = (data.prompt_results || []).map(d => `
            <div class="rt-row">
                <span style="flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${esc(d.prompt)}</span>
                <span class="badge badge-${d.action}" style="margin-left:.5rem;flex-shrink:0">${d.action}</span>
            </div>
        `).join("");
    }

    // ============================================================
    // PILLAR 2: Trustworthiness Scorecard
    // ============================================================
    const kpiTotal = document.getElementById("kpi-total");
    const kpiBlocked = document.getElementById("kpi-blocked");
    const kpiWarned = document.getElementById("kpi-warned");
    const kpiAllowed = document.getElementById("kpi-allowed");
    const kpiTrust = document.getElementById("kpi-trust");

    async function refreshScorecard() {
        try {
            const res = await fetch(`${API}/scorecard?tenant_id=default`);
            const data = await res.json();
            const counts = data.action_counts;
            const total = Object.values(counts).reduce((a, b) => a + b, 0);
            kpiTotal.textContent = total;
            kpiBlocked.textContent = counts.block || 0;
            kpiWarned.textContent = counts.warn || 0;
            kpiAllowed.textContent = (counts.allow || 0) + (counts.sanitize || 0);
            kpiTrust.textContent = data.trust_score;

            // Dimensions
            if (data.dimensions && data.dimensions.length > 0) {
                document.getElementById("dimensions-grid").innerHTML = data.dimensions.map(dim => {
                    const color = dim.score >= 8 ? "var(--green)" : dim.score >= 5 ? "var(--amber)" : "var(--red)";
                    return `
                        <div class="dimension-card">
                            <div class="dim-name">${esc(dim.name)}</div>
                            <div class="dim-score" style="color:${color}">${dim.score}</div>
                            <div class="dim-detail">${esc(dim.detail)}</div>
                        </div>
                    `;
                }).join("");
            }
        } catch { /* ignore */ }
    }

    // ============================================================
    // PILLAR 3: Ethics Layer Plugin
    // ============================================================
    const promptInput = document.getElementById("prompt-input");
    const tenantSelect = document.getElementById("tenant-select");
    const btnTest = document.getElementById("btn-test");
    const resultPanel = document.getElementById("result-panel");
    const resultAction = document.getElementById("result-action");
    const resultScore = document.getElementById("result-score");
    const resultExpl = document.getElementById("result-explanation");
    const resultLabels = document.getElementById("result-labels");
    const pipelineTrace = document.getElementById("pipeline-trace");

    btnTest.addEventListener("click", async () => {
        const prompt = promptInput.value.trim();
        if (!prompt) return;
        btnTest.disabled = true;
        btnTest.textContent = "⏳ Evaluating...";

        try {
            const res = await fetch(`${API}/filter`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    tenant_id: tenantSelect.value,
                    session_id: "dashboard_" + Date.now(),
                    prompt: prompt
                })
            });
            const data = await res.json();
            showResult(data);
            showPipelineTrace(data.pipeline_trace || []);
        } catch (err) { alert("Error: " + err.message); }
        finally {
            btnTest.disabled = false;
            btnTest.textContent = "⚡ Evaluate";
        }
    });

    function showResult(data) {
        resultPanel.classList.remove("hidden");
        const actionClass = { block: "badge-block", warn: "badge-warn", allow: "badge-allow", sanitize: "badge-sanitize" }[data.action] || "badge-allow";
        resultAction.className = "badge " + actionClass;
        resultAction.textContent = data.action.toUpperCase();
        resultScore.textContent = data.risk_score.toFixed(2);
        resultScore.style.color = data.risk_score > 0.7 ? "var(--red)" : data.risk_score > 0.4 ? "var(--amber)" : "var(--green)";
        resultExpl.textContent = data.explanation;
        resultLabels.innerHTML = data.labels.map(l => `<span class="label-chip">${l}</span>`).join("");
    }

    function showPipelineTrace(trace) {
        if (trace.length === 0) {
            pipelineTrace.innerHTML = '<p class="empty-state">No trace data available.</p>';
            return;
        }
        pipelineTrace.innerHTML = trace.map((step, i) => {
            const riskColor = step.risk_contributed > 0.7 ? "var(--red)" : step.risk_contributed > 0.3 ? "var(--amber)" : "var(--green)";
            return `
                <div class="trace-step">
                    <div class="trace-step-header">
                        <span class="trace-stage">Stage ${i + 1}: ${esc(step.stage)}</span>
                        <span class="trace-risk" style="color:${riskColor}">Risk: ${step.risk_contributed.toFixed(2)}</span>
                    </div>
                    <div class="trace-reason">${esc(step.reason)}</div>
                    <div class="trace-labels">
                        ${step.labels_added.map(l => `<span class="label-chip">${l}</span>`).join("") || '<span style="font-size:.72rem;color:var(--text-dim)">No labels added</span>'}
                    </div>
                </div>
            `;
        }).join("");
    }

    // ============================================================
    // PILLAR 4: LLM Audit API
    // ============================================================
    const auditBody = document.getElementById("audit-body");

    async function refreshAudit() {
        try {
            const res = await fetch(`${API}/audit/logs?tenant_id=default&size=100`);
            const data = await res.json();
            if (data.logs.length === 0) {
                auditBody.innerHTML = `<tr><td colspan="7" class="empty-state">No audit entries yet.</td></tr>`;
                return;
            }
            auditBody.innerHTML = data.logs.reverse().map(log => `
                <tr>
                    <td style="white-space:nowrap">${new Date(log.timestamp).toLocaleTimeString()}</td>
                    <td>${esc(log.tenant_id)}</td>
                    <td style="max-width:180px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${esc(log.prompt_snippet || log.session_id)}</td>
                    <td><span class="badge badge-${log.action}">${log.action}</span></td>
                    <td>${log.risk_score.toFixed(2)}</td>
                    <td>${log.labels.map(l => `<span class="label-chip" style="margin-right:2px">${l}</span>`).join("") || "—"}</td>
                    <td style="max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:.72rem;color:var(--text-dim)">${esc(log.explanation || "—")}</td>
                </tr>
            `).join("");
        } catch { /* ignore */ }
    }

    // Utility
    function esc(str) {
        if (!str) return "";
        const d = document.createElement("div");
        d.textContent = str;
        return d.innerHTML;
    }

    // Initial refresh
    refreshScorecard();
})();
