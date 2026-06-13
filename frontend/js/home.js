import { fetchJson, requireOnboarding, renderNav, formatMoney, dataSourceBadge } from "./app.js";

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
      html: 'Open <a href="/static/learn.html">Learn</a> and finish lesson 1 (15/65/20 cash flow machine).',
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

function renderFinancialReality(summary) {
  document.getElementById("data-badge").innerHTML = dataSourceBadge(summary.data_source);
  document.getElementById("reality-grid").innerHTML = `
    <div><span class="label">Income</span><strong>${formatMoney(summary.monthly_gross_income)}</strong></div>
    <div><span class="label">Essentials</span><strong>${formatMoney(summary.monthly_essentials)}</strong></div>
    <div><span class="label">Debt total</span><strong>${formatMoney(summary.debt_total)}</strong></div>
    <div><span class="label">Stability Fund</span><strong>${summary.stability_fund.pct_of_target}%</strong></div>
    <div><span class="label">Credit band</span><strong>${summary.credit_plan.score_band}</strong></div>
    <div><span class="label">Loan readiness</span><strong>${summary.credit_plan.loan_readiness_score}/100</strong></div>`;
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

    const selfTrust = await fetchJson("/reputation/self-trust");
    renderStartGuide(profile, journey, selfTrust);

    const quickWins = await fetchJson("/user/intake/quick-wins");
    renderQuickWins(quickWins);

    await loadForkMoments();

    const mirror = await fetchJson(`/dashboard/mirror?stability_fund_pct=${journey.stability_fund_pct || 0}`);
    document.getElementById("identity-line").textContent ||= mirror.identity_line;
    document.getElementById("solitude-integrity").textContent = mirror.silent_kpis.reputation_credit_score.toFixed(0);
    document.getElementById("deep-work").textContent = profile.creation_hour || "—";
  } catch (e) {
    document.getElementById("error").textContent = e.message;
  }
});
