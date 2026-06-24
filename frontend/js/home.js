import { fetchJson, requireOnboarding, renderNav, formatMoney, dataSourceBadge, renderEsbiPanel } from "./app.js";

let pendingPauseId = null;

function renderStartGuide(profile, journey, selfTrust) {
  const literacy = profile.literacy_completed || [];
  const lessonDone = literacy.length > 0;
  const hasCommitment = (selfTrust.active_commitments || []).length > 0;
  const hasCheckIn = (selfTrust.commitments_set || 0) > 0;

  const steps = [
    {
      done: profile.onboarding_completed,
      html: 'Complete <a href="/static/onboarding.html">Financial Reality Intake</a> — your income, debts, credit, business budget.',
    },
    {
      done: lessonDone,
      html: 'Open <a href="/static/learn.html">Learn</a> — complete lesson 1 (objectives + exercise checklist, not just a phrase).',
    },
    {
      done: hasCommitment,
      html: 'On <a href="/static/integrity.html">Your Integrity</a>, set one private promise (wake time, learning block, or pause rule).',
    },
    {
      done: hasCheckIn,
      html: "Weekly: check in Kept/Missed on that promise — that's what moves Self-Trust off 50.",
    },
    {
      done: false,
      html: `Stage: <strong>${journey.stage || "Stability"}</strong> — ${journey.next_mechanical_action || "fund Stability Fund."}`,
    },
    {
      done: false,
      html: 'Try <a href="/static/advisor.html">Ask Advisor</a> (AI chat — run <code>python server.py</code>, not mechanical-only).',
    },
  ];

  document.getElementById("start-steps").innerHTML = steps
    .map((s) => `<li class="${s.done ? "done" : ""}">${s.done ? "✓ " : ""}${s.html}</li>`)
    .join("");
}

function renderBreakdownList(items, labelKey, amountKey) {
  if (!items?.length) return "";
  return `<ul class="breakdown-list">${items
    .map(
      (x) =>
        `<li><span>${x[labelKey]}</span><strong>${formatMoney(x[amountKey])}</strong></li>`
    )
    .join("")}</ul>`;
}

function renderCreditPanel(summary) {
  const credit = summary.credit_plan || {};
  const snap = summary.credit_snapshot || {};
  const items = credit.collections_items || snap.collections_items || [];
  const flags = credit.flags || [];
  const actions = credit.weekly_actions || [];
  const hasCreditDetail =
    items.length ||
    flags.length ||
    actions.length ||
    credit.charge_offs ||
    credit.bankruptcies ||
    (credit.inquiries_6mo || 0) > 0 ||
    snap.total_credit_limit ||
    snap.estimated_score;

  const el = document.getElementById("reality-credit");
  if (!el) return;
  el.classList.toggle("hidden", !hasCreditDetail);

  const collectionsHtml = items.length
    ? `<ul class="breakdown-list">${items
        .map(
          (c) =>
            `<li><span>${c.creditor} <span class="muted small">(${c.status || "open"})</span></span><strong>${formatMoney(c.balance)}</strong></li>`
        )
        .join("")}</ul>`
    : "";

  const flagsHtml = flags.length
    ? `<ul class="credit-flags">${flags.map((f) => `<li>${f}</li>`).join("")}</ul>`
    : "";
  const actionsHtml = actions.length
    ? `<ul class="credit-actions">${actions.map((a) => `<li>${a}</li>`).join("")}</ul>`
    : "";

  el.innerHTML = `
    <h3 class="form-sub">Credit & collections</h3>
    <div class="credit-grid">
      <div><span class="label">Estimated score</span><strong>${snap.estimated_score || credit.estimated_score_midpoint || "—"}</strong></div>
      <div><span class="label">Utilization</span><strong>${credit.utilization_pct ?? snap.utilization_pct ?? 0}%</strong></div>
      <div><span class="label">Credit limits</span><strong>${formatMoney(snap.total_credit_limit || 0)}</strong></div>
      <div><span class="label">Revolving balance</span><strong>${formatMoney(snap.total_revolver_balance || 0)}</strong></div>
      <div><span class="label">Collections balance</span><strong>${formatMoney(credit.collections_balance || 0)}</strong></div>
      <div><span class="label">Charge-offs</span><strong>${credit.charge_offs ?? snap.charge_offs ?? 0}</strong></div>
      <div><span class="label">Bankruptcies</span><strong>${credit.bankruptcies ?? snap.bankruptcies ?? 0}</strong></div>
      <div><span class="label">Inquiries (6 mo)</span><strong>${credit.inquiries_6mo ?? snap.inquiries_6mo ?? 0}</strong></div>
    </div>
    ${collectionsHtml ? `<div class="breakdown-block"><h4 class="form-sub">Collection accounts</h4>${collectionsHtml}</div>` : ""}
    ${flagsHtml ? `<div class="breakdown-block"><h4 class="form-sub">Flags</h4>${flagsHtml}</div>` : ""}
    ${actionsHtml ? `<div class="breakdown-block"><h4 class="form-sub">This week</h4>${actionsHtml}</div>` : ""}`;
}

function renderFinancialReality(summary) {
  document.getElementById("data-badge").innerHTML = dataSourceBadge(summary.data_source);
  const income = summary.income_breakdown;
  const expense = summary.expense_breakdown;
  const incomeDetail = income?.streams?.length
    ? renderBreakdownList(
        income.streams.map((s) => ({ label: `${s.name} (${s.source_type})`, amount: s.amount_monthly })),
        "label",
        "amount"
      )
    : "";
  const expenseCats = expense?.by_category_labeled
    ? renderBreakdownList(
        Object.entries(expense.by_category_labeled).map(([label, amount]) => ({ label, amount })),
        "label",
        "amount"
      )
    : "";
  const billsDetail = expense?.bills?.length
    ? renderBreakdownList(expense.bills, "name", "amount_monthly")
    : "";

  document.getElementById("reality-grid").innerHTML = `
    <div><span class="label">Monthly income</span><strong>${formatMoney(summary.monthly_gross_income)}</strong></div>
    <div><span class="label">Monthly essentials</span><strong>${formatMoney(summary.monthly_essentials)}</strong></div>
    <div><span class="label">Debt total</span><strong>${formatMoney(summary.debt_total)}</strong></div>
    <div><span class="label">Stability Fund</span><strong>${summary.stability_fund.pct_of_target}%</strong></div>
    <div><span class="label">Credit band</span><strong>${summary.credit_plan.score_band}</strong></div>
    <div><span class="label">Loan readiness</span><strong>${summary.credit_plan.loan_readiness_score}/100</strong></div>`;

  const breakdownEl = document.getElementById("reality-breakdowns");
  if (breakdownEl) {
    const hasDetail = incomeDetail || expenseCats || billsDetail;
    breakdownEl.classList.toggle("hidden", !hasDetail);
    breakdownEl.innerHTML = hasDetail
      ? `
      ${incomeDetail ? `<div class="breakdown-block"><h3 class="form-sub">Income sources</h3>${incomeDetail}</div>` : ""}
      ${expenseCats ? `<div class="breakdown-block"><h3 class="form-sub">Expense categories</h3>${expenseCats}</div>` : ""}
      ${billsDetail ? `<div class="breakdown-block"><h3 class="form-sub">Recurring bills</h3>${billsDetail}</div>` : ""}`
      : "";
  }

  renderCreditPanel(summary);

  const snow = summary.debt_snowball;
  document.getElementById("snowball-line").textContent = snow.primary_target
    ? `Debt snowball #1: ${snow.primary_target} @ ${snow.guaranteed_return_pct}% APR — ${snow.rule}`
    : snow.message || "";
}

function renderQuickWins(data) {
  document.getElementById("quick-wins-list").innerHTML = (data.quick_wins || [])
    .map((w) => `<li><strong>${w.title}</strong> — ${w.action}</li>`)
    .join("");
  document.getElementById("opportunities-list").innerHTML = (data.opportunities || [])
    .map(
      (o) =>
        `<li class="${o.gated ? "muted" : ""}"><strong>${o.title}</strong>${o.gated ? " (locked)" : ""} — ${o.action}</li>`
    )
    .join("");
}

function formatMemoryDate(iso) {
  if (!iso) return "";
  try {
    return new Date(iso).toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" });
  } catch {
    return "";
  }
}

async function renderMemoryPanel() {
  const factsEl = document.getElementById("memory-facts");
  const emptyEl = document.getElementById("memory-empty");
  const summaryEl = document.getElementById("memory-summary");
  const snapshotsEl = document.getElementById("memory-snapshots");

  let dossier;
  let factsData;
  let chatData;
  let snapshotsData;

  try {
    [dossier, factsData, chatData, snapshotsData] = await Promise.all([
      fetchJson("/user/memory/dossier"),
      fetchJson("/user/memory/facts"),
      fetchJson("/user/memory/chat").catch(() => ({ count: 0 })),
      fetchJson("/user/memory/snapshots").catch(() => ({ snapshots: [] })),
    ]);
  } catch {
    summaryEl.innerHTML = `<p class="muted small">Memory loads when the full server is running (<code>python server.py</code>).</p>`;
    factsEl.innerHTML = "";
    snapshotsEl.innerHTML = "";
    emptyEl.classList.add("hidden");
    return;
  }

  const identity = dossier.architect_identity || {};
  const journey = dossier.journey || {};
  const cq = dossier.financial_summary?.cashflow_quadrant || journey.cashflow_quadrant;
  const facts = factsData.facts || [];
  const snapshots = snapshotsData.snapshots || [];

  summaryEl.innerHTML = `
    <div><span class="label">Architect</span><strong>${identity.display_name || "You"}</strong></div>
    <div><span class="label">Stage</span><strong>${journey.stage || "—"}</strong></div>
    ${cq ? `<div><span class="label">Cashflow quadrant</span><strong>${cq.badge || "—"}</strong></div>` : ""}
    <div><span class="label">Saved facts</span><strong>${facts.length}</strong></div>
    <div><span class="label">Chat messages</span><strong>${chatData.count ?? 0}</strong></div>`;

  if (!facts.length) {
    factsEl.innerHTML = "";
    emptyEl.classList.remove("hidden");
  } else {
    emptyEl.classList.add("hidden");
    factsEl.innerHTML = facts
      .map(
        (f) => `
      <li>
        <div class="memory-fact-body">
          <span class="memory-tag">${f.category || "general"}</span>
          ${f.content}
          <span class="small muted"> · ${formatMemoryDate(f.created_at)}${f.source_agent ? ` · ${f.source_agent}` : ""}</span>
        </div>
        <button type="button" class="btn btn-secondary btn-sm memory-forget" data-id="${f.id}">Forget</button>
      </li>`
      )
      .join("");

    factsEl.querySelectorAll(".memory-forget").forEach((btn) => {
      btn.onclick = async () => {
        if (!confirm("Remove this remembered fact?")) return;
        await fetchJson(`/user/memory/facts/${btn.dataset.id}`, { method: "DELETE" });
        await renderMemoryPanel();
      };
    });
  }

  if (!snapshots.length) {
    snapshotsEl.innerHTML = `<li class="muted">No progress snapshots yet — open Ask Advisor to start tracking.</li>`;
  } else {
    snapshotsEl.innerHTML = snapshots
      .slice(0, 5)
      .map((s) => {
        const fund = s.metrics?.stability_fund_pct;
        const fundTxt = fund != null ? `${fund}% Stability Fund` : "";
        return `<li><strong>${s.stage}</strong> — ${formatMemoryDate(s.created_at)}${fundTxt ? ` · ${fundTxt}` : ""}${s.note ? `<br /><span class="small">${s.note}</span>` : ""}</li>`;
      })
      .join("");
  }
}

document.getElementById("nav").innerHTML = renderNav("home");

function applySolitudeMode(active) {
  document.getElementById("main-standard").classList.toggle("hidden", active);
  document.getElementById("main-solitude").classList.toggle("hidden", !active);
  document.body.classList.toggle("solitude-mode", active);
  document.getElementById("nav").classList.toggle("hidden", active);
}

async function loadForkMoments() {
  const data = await fetchJson("/mirror/fork-moments");
  const el = document.getElementById("active-pauses");
  if (!data.active_pauses.length) {
    el.innerHTML = '<p class="muted small">No active pauses.</p>';
    return;
  }
  el.innerHTML = data.active_pauses
    .map(
      (p) => `
    <div class="pause-card">
      <strong>${p.item}</strong> — ${formatMoney(p.amount)}
      <span class="small muted">${Math.round(p.hours_remaining)}h until unlock</span>
      ${p.identity_notification ? `<p class="identity small">${p.identity_notification}</p>` : ""}
      ${!p.emotion_acknowledged ? `<button type="button" class="btn btn-secondary btn-sm ack-emotion" data-id="${p.id}">Acknowledge emotion</button>` : ""}
    </div>`
    )
    .join("");
  el.querySelectorAll(".ack-emotion").forEach((btn) => {
    btn.onclick = () => {
      pendingPauseId = Number(btn.dataset.id);
      document.getElementById("emotion-panel").classList.remove("hidden");
    };
  });
}

requireOnboarding().then(async (profile) => {
  if (!profile) return;

  const welcome = sessionStorage.getItem("welcome_message");
  if (welcome) {
    document.getElementById("welcome-banner").textContent = welcome;
    document.getElementById("welcome-banner").classList.remove("hidden");
    sessionStorage.removeItem("welcome_message");
  }

  document.getElementById("greeting").textContent = `Command Center`;
  document.getElementById("focus-toggle").checked = profile.solitude_mode_active;
  document.getElementById("creation-hour").value = profile.creation_hour || "07:00";
  applySolitudeMode(profile.solitude_mode_active);

  document.getElementById("focus-save").onclick = async () => {
    const res = await fetchJson("/user/focus-season", {
      method: "POST",
      body: JSON.stringify({
        active: document.getElementById("focus-toggle").checked,
        creation_hour: document.getElementById("creation-hour").value,
      }),
    });
    document.getElementById("focus-msg").textContent = res.identity_notification;
    applySolitudeMode(res.solitude_mode_active);
  };

  document.getElementById("fork-form").onsubmit = async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    const res = await fetchJson("/mirror/fork-moments/pause", {
      method: "POST",
      body: JSON.stringify({
        item_description: fd.get("item"),
        amount: Number(fd.get("amount")),
        bucket: "life",
      }),
    });
    if (res.status === "paused") {
      pendingPauseId = res.pause_id;
      document.getElementById("emotion-panel").classList.remove("hidden");
      e.target.reset();
      await loadForkMoments();
    }
  };

  document.querySelectorAll(".emotion-btns button").forEach((btn) => {
    btn.onclick = async () => {
      if (!pendingPauseId) return;
      const res = await fetchJson("/mirror/fork-moments/acknowledge", {
        method: "POST",
        body: JSON.stringify({
          pause_id: pendingPauseId,
          emotion: btn.dataset.emotion,
          choose_architect_path: true,
        }),
      });
      document.getElementById("identity-line").textContent = res.identity_notification;
      document.getElementById("emotion-panel").classList.add("hidden");
      pendingPauseId = null;
      await loadForkMoments();
    };
  });

  document.getElementById("reset-profile").onclick = async () => {
    if (!confirm("Clear all your data and start intake again?")) return;
    await fetchJson("/user/intake/reset", { method: "POST" });
    window.location.href = "/static/get-started.html";
  };

  try {
    const summary = await fetchJson("/user/intake/summary");
    renderFinancialReality(summary);

    const missions = await fetchJson("/mirror/dollar-missions");
    document.getElementById("gap-message").textContent = missions.gap_message;
    document.getElementById("missions-list").innerHTML = missions.missions
      .map(
        (m) =>
          `<li><strong>${m.job}</strong> — ${formatMoney(m.amount)} <span class="muted">(${m.rule})</span></li>`
      )
      .join("");

    const journey = await fetchJson("/user/journey");
    document.getElementById("stage-name").textContent = journey.stage;
    document.getElementById("stage-progress").style.width = `${(journey.stage_index / journey.total_stages) * 100}%`;
    document.getElementById("next-action").textContent = journey.next_mechanical_action;
    renderEsbiPanel(journey.cashflow_quadrant);

    const selfTrust = await fetchJson("/reputation/self-trust");
    renderStartGuide(profile, journey, selfTrust);

    const quickWins = await fetchJson("/user/intake/quick-wins");
    renderQuickWins(quickWins);

    await renderMemoryPanel();

    await loadForkMoments();

    const mirror = await fetchJson(`/dashboard/mirror?stability_fund_pct=${journey.stability_fund_pct || 0}`);
    document.getElementById("identity-line").textContent ||= mirror.identity_line;
    document.getElementById("solitude-integrity").textContent = mirror.silent_kpis.reputation_credit_score.toFixed(0);
    document.getElementById("deep-work").textContent = profile.creation_hour || "—";
  } catch (e) {
    document.getElementById("error").textContent = e.message;
  }
});
