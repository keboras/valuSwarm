import { fetchJson } from "./app.js";

const TOTAL = 7;
let step = 1;
const debts = [];
const footprints = { banking: false, calendar: false, screen_time: false };

function showStep() {
  for (let i = 1; i <= TOTAL; i++) {
    document.getElementById(`step-${i}`)?.classList.toggle("hidden", i !== step);
  }
  document.getElementById("step-label").textContent = `Step ${step} of ${TOTAL}`;
  document.getElementById("btn-back").classList.toggle("hidden", step === 1);
  document.getElementById("btn-next").textContent = step === TOTAL ? "Begin as Architect" : "Save & continue";
}

function renderDebts() {
  const el = document.getElementById("debt-list");
  if (!debts.length) {
    el.innerHTML = '<p class="muted small">No debts added — click Add debt or continue if debt-free.</p>';
    return;
  }
  el.innerHTML = debts
    .map(
      (d, i) => `
    <div class="pattern-card" data-idx="${i}">
      <strong>${d.name}</strong> — $${d.balance} @ ${d.apr}% APR (min $${d.minimum_payment})
      <button type="button" class="btn btn-secondary btn-sm remove-debt" data-idx="${i}">Remove</button>
    </div>`
    )
    .join("");
  el.querySelectorAll(".remove-debt").forEach((btn) => {
    btn.onclick = () => {
      debts.splice(Number(btn.dataset.idx), 1);
      renderDebts();
    };
  });
}

document.getElementById("add-debt").onclick = () => {
  const name = prompt("Debt name (e.g. Chase Visa)");
  if (!name) return;
  const balance = Number(prompt("Balance ($)", "0"));
  const apr = Number(prompt("APR (%)", "0"));
  const minimum_payment = Number(prompt("Minimum payment ($)", "0"));
  debts.push({
    name,
    balance: isNaN(balance) ? 0 : balance,
    apr: isNaN(apr) ? 0 : apr,
    minimum_payment: isNaN(minimum_payment) ? 0 : minimum_payment,
    secured: false,
  });
  renderDebts();
};

document.querySelectorAll(".connect-btn").forEach((btn) => {
  btn.onclick = () => {
    const source = btn.dataset.source;
    footprints[source] = !footprints[source];
    btn.classList.toggle("connected", footprints[source]);
    const active = Object.entries(footprints)
      .filter(([, v]) => v)
      .map(([k]) => k.replace("_", " "))
      .join(", ");
    document.getElementById("connect-status").textContent = active
      ? `Optional footprints: ${active}`
      : "Skip or connect demo footprints for behavioral patterns.";
  };
});

function formData(form) {
  return Object.fromEntries(new FormData(form).entries());
}

async function saveStep(n, body) {
  const res = await fetchJson(`/user/intake/step/${n}`, {
    method: "POST",
    body: JSON.stringify(body),
  });
  if (res.preview) {
    const p = res.preview;
    document.getElementById("preview-box").classList.remove("hidden");
    document.getElementById("preview-box").innerHTML = `
      <strong>Preview:</strong> 15/65/20 → Future $${p.allocation_156520?.future?.toLocaleString() ?? "—"} |
      Stability Fund ${p.stability_fund?.pct_of_target ?? 0}% of target
      ${p.debt_snowball?.primary_target ? ` | Snowball target: ${p.debt_snowball.primary_target}` : ""}`;
  }
  return res;
}

async function collectAndSave(current) {
  if (current === 1) {
    const fd = formData(document.getElementById("form-1"));
    if (!fd.display_name?.trim()) throw new Error("Enter your name.");
    await saveStep(1, fd);
  } else if (current === 2) {
    const fd = formData(document.getElementById("form-2"));
    await saveStep(2, {
      monthly_gross_income: Number(fd.monthly_gross_income),
      monthly_essentials: Number(fd.monthly_essentials),
      stability_fund_balance: Number(fd.stability_fund_balance || 0),
      stability_fund_target_months: Number(fd.stability_fund_target_months),
    });
  } else if (current === 3) {
    await saveStep(3, { debts });
  } else if (current === 4) {
    const fd = formData(document.getElementById("form-4"));
    await saveStep(4, {
      score_band: fd.score_band,
      utilization_pct: Number(fd.utilization_pct || 0),
      late_payments_12mo: !!document.querySelector('[name="late_payments_12mo"]').checked,
      collections: !!document.querySelector('[name="collections"]').checked,
    });
  } else if (current === 5) {
    const fd = formData(document.getElementById("form-5"));
    const total =
      Number(fd.profit_pct) + Number(fd.tax_pct) + Number(fd.owner_pay_pct) + Number(fd.opex_pct);
    if (Math.abs(total - 100) > 0.5) throw new Error("Business budget percentages must sum to 100.");
    await saveStep(5, {
      business_type: fd.business_type,
      monthly_revenue: Number(fd.monthly_revenue || 0),
      profit_pct: Number(fd.profit_pct),
      tax_pct: Number(fd.tax_pct),
      owner_pay_pct: Number(fd.owner_pay_pct),
      opex_pct: Number(fd.opex_pct),
    });
  } else if (current === 6) {
    await saveStep(6, { footprints });
  }
}

document.getElementById("btn-back").onclick = () => {
  if (step > 1) {
    step -= 1;
    showStep();
  }
};

document.getElementById("btn-next").onclick = async () => {
  document.getElementById("error").textContent = "";
  try {
    if (step < TOTAL) {
      await collectAndSave(step);
      step += 1;
      showStep();
      return;
    }
    if (!document.getElementById("contract-check").checked) {
      document.getElementById("error").textContent = "Sign the contract to continue.";
      return;
    }
    const result = await fetchJson("/user/intake/complete", {
      method: "POST",
      body: JSON.stringify({ display_name: "Architect", focus_season_months: 6 }),
    });
    sessionStorage.setItem("welcome_message", result.identity_notification);
    window.location.href = "/static/index.html";
  } catch (e) {
    document.getElementById("error").textContent = e.message;
  }
};

(async () => {
  try {
    const status = await fetchJson("/user/intake/status");
    if (status.intake_completed) {
      window.location.href = "/static/index.html";
      return;
    }
    if (status.intake_step > 0) {
      step = Math.min(status.intake_step + 1, TOTAL);
    }
  } catch {
    /* new user */
  }
  renderDebts();
  showStep();
})();
