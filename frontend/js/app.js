// Shared app utilities — onboarding gate, navigation, user profile

const API_BASE = window.API_BASE ?? "";

export async function fetchJson(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text();
    if (/traceback/i.test(text) || text.includes('File "') || text.includes("File '")) {
      throw new Error("Something went wrong. Try again.");
    }
    throw new Error(text || res.statusText);
  }
  return res.json();
}

export function pillarBar(label, value, weight) {
  return `
    <div class="pillar">
      <div class="pillar-head">
        <span>${label}</span>
        <span>${value.toFixed(1)}</span>
      </div>
      <div class="bar"><div class="fill" style="width:${Math.min(value, 100)}%"></div></div>
    </div>`;
}

export function tierClass(tier) {
  return `tier tier-${(tier || "bronze").toLowerCase()}`;
}

const STATIONS = [
  { id: "home", n: "01", href: "/static/index.html", label: "Today" },
  { id: "learn", n: "02", href: "/static/learn.html", label: "Learn" },
  { id: "integrity", n: "03", href: "/static/integrity.html", label: "Integrity" },
  { id: "studio", n: "04", href: "/static/studio.html", label: "Studio" },
  { id: "advisor", n: "05", href: "/static/advisor.html", label: "Ask" },
];

export function renderNav(active) {
  const stations = STATIONS.map((s) => {
    const sub =
      s.id === "home" && active === "home"
        ? `<div class="ow-sub" role="tablist" aria-label="Today layers">
            <button type="button" class="deck-btn active" data-deck="pulse" role="tab"><span>1.1</span> Numbers</button>
            <button type="button" class="deck-btn" data-deck="moves" role="tab"><span>1.2</span> Move</button>
            <button type="button" class="deck-btn" data-deck="desk" role="tab"><span>1.3</span> Pause</button>
          </div>`
        : "";
    return `<div class="ow-station-block${s.id === "advisor" ? " is-quiet" : ""}">
      <a class="ow-station${active === s.id ? " is-on" : ""}" href="${s.href}" data-station="${s.n}" ${active === s.id ? 'aria-current="page"' : ""}>
        <span class="ow-n">${s.n}</span>
        <span class="ow-l">${s.label}</span>
      </a>
      ${sub}
    </div>`;
  }).join("");
  return `<a class="ow-mark" href="/static/index.html" aria-label="OmniWealth — Today">
      <b>OW</b>
      <em>OmniWealth</em>
    </a>
    <p class="ow-pledge">You execute.</p>
    <nav class="ow-stations" aria-label="Stations">${stations}</nav>
    <p class="ow-keys"><kbd>1</kbd>–<kbd>5</kbd> jump</p>`;
}

export function mountShell(active) {
  document.body.classList.add("ow");
  const el = document.getElementById("nav");
  if (!el) return;
  el.classList.add("ow-rail");
  el.innerHTML = renderNav(active);
  bindStationKeys();
}

function bindStationKeys() {
  if (window.__owKeys) return;
  window.__owKeys = true;
  document.addEventListener("keydown", (e) => {
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    const tag = (e.target && e.target.tagName) || "";
    if (/INPUT|TEXTAREA|SELECT/.test(tag) || e.target?.isContentEditable) return;
    const map = { 1: "/static/index.html", 2: "/static/learn.html", 3: "/static/integrity.html", 4: "/static/studio.html", 5: "/static/advisor.html" };
    const href = map[e.key];
    if (href) window.location.href = href;
  });
}

export async function requireOnboarding() {
  const path = window.location.pathname;
  if (path.includes("get-started.html") || path.includes("onboarding.html")) return null;
  try {
    const profile = await fetchJson("/user/profile");
    const done = profile.intake_completed || profile.onboarding_completed;
    if (!done) {
      window.location.href = "/static/get-started.html";
      return null;
    }
    return profile;
  } catch {
    return null;
  }
}

export function formatMoney(n) {
  return new Intl.NumberFormat(undefined, { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(n);
}

export function dataSourceBadge(source) {
  if (source === "manual") return '<span class="badge">Your data</span>';
  if (source === "demo") return '<span class="badge badge-demo">Demo data</span>';
  return `<span class="badge badge-demo">${source || "Unknown"}</span>`;
}

const ESBI_LABELS = { E: "Employee", S: "Self-employed", B: "Business owner", I: "Investor" };

export function renderEsbiCell(key, cq) {
  const mix = cq.income_mix_pct || {};
  const pct = Math.round(mix[key] || 0);
  const isPrimary = cq.primary_quadrant === key;
  const isTarget = cq.target_quadrant === key;
  const tags = [];
  if (isPrimary) tags.push('<span class="esbi-cell-tag">You</span>');
  if (isTarget && !isPrimary) tags.push('<span class="esbi-cell-tag target-tag">Target</span>');
  if (isTarget && isPrimary) tags.push('<span class="esbi-cell-tag target-tag">Deepen</span>');
  const classes = ["esbi-cell", isPrimary ? "primary" : "", isTarget ? "target" : ""].filter(Boolean).join(" ");
  return `
    <div class="${classes}" data-quadrant="${key}">
      ${tags.join("")}
      <div>
        <div class="esbi-cell-letter">${key}</div>
        <div class="esbi-cell-label">${ESBI_LABELS[key]}</div>
      </div>
      <div class="esbi-cell-pct">${pct}%</div>
    </div>`;
}

export function buildEsbiGridHtml(cq) {
  return `
    ${renderEsbiCell("E", cq)}
    ${renderEsbiCell("B", cq)}
    ${renderEsbiCell("S", cq)}
    ${renderEsbiCell("I", cq)}
    <p class="esbi-mix-summary" style="grid-column: 1 / -1;">
      Left (time): <strong>${cq.left_side_pct ?? 0}%</strong>
      · Right (systems): <strong>${cq.right_side_pct ?? 0}%</strong>
    </p>`;
}

export function renderEsbiPanel(cq, gridId = "esbi-grid") {
  const panel = document.getElementById("esbi-panel");
  if (!panel || !cq) return;
  panel.classList.remove("hidden");
  document.getElementById("esbi-badge").textContent = cq.badge || "—";
  const grid = document.getElementById(gridId);
  if (grid) grid.innerHTML = buildEsbiGridHtml(cq);
  const primaryEl = document.getElementById("esbi-primary");
  const nextEl = document.getElementById("esbi-next");
  if (primaryEl) {
    primaryEl.textContent =
      `${cq.primary_label || ""} (${cq.primary_side || "left"} side) · Target: ${cq.target_label || ""} — ${cq.transition || ""}`;
  }
  if (nextEl) nextEl.textContent = cq.next_mechanical_move || "";
}

export function renderAdvisorEsbiContext(cq) {
  const el = document.getElementById("esbi-context");
  if (!el || !cq) return;
  el.classList.remove("hidden");
  el.innerHTML = `
    <div class="esbi-context-head">
      <h2>Cashflow Quadrant <span class="esbi-badge">${cq.badge || ""}</span></h2>
      <span class="small muted">${cq.primary_label} → ${cq.target_label}</span>
    </div>
    <div class="esbi-grid-wrap">
      <div class="esbi-grid">${buildEsbiGridHtml(cq)}</div>
    </div>
    <p class="small muted">${cq.next_mechanical_move || ""}</p>`;
}

export function formatEsbiInstructions(cq) {
  if (!cq) return "";
  const mix = cq.income_mix_pct || {};
  const mixLine = ["E", "S", "B", "I"].map((k) => `${k}=${mix[k] ?? 0}%`).join(", ");
  return (
    `Cashflow Quadrant (ESBI) — always reference when discussing wealth path:\n` +
    `- Primary: ${cq.primary_quadrant} (${cq.primary_label}). Target: ${cq.target_quadrant} (${cq.target_label}). Badge: ${cq.badge}.\n` +
    `- Income mix: ${mixLine}. Left ${cq.left_side_pct}% / Right ${cq.right_side_pct}%.\n` +
    `- Next ESBI move: ${cq.next_mechanical_move}\n` +
    `- This is NOT Covey Quadrant II (time management).\n`
  );
}
