// Shared app utilities — onboarding gate, navigation, user profile

const API_BASE = window.API_BASE ?? "";

export async function fetchJson(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text();
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

export function renderNav(active) {
  const links = [
    { id: "home", href: "/static/index.html", label: "Command Center" },
    { id: "learn", href: "/static/learn.html", label: "Learn" },
    { id: "integrity", href: "/static/integrity.html", label: "Your Integrity" },
    { id: "advisor", href: "/static/advisor.html", label: "Ask Advisor" },
  ];
  return links
    .map(
      (l) =>
        `<a href="${l.href}" class="${active === l.id ? "active" : ""}">${l.label}</a>`
    )
    .join("");
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
