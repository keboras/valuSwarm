import { fetchJson, requireOnboarding, renderNav } from "./app.js";

const FALLBACK_MODULES = [
  {
    id: "architect-not-engine",
    order: 1,
    title: "You Are the Architect, Not the Engine",
    summary: "Your job is to design systems.",
    body: "Self-employed people trade hours for money until they build a machine that runs without them.",
    key_point: "If your money depends on your presence, your freedom is temporary.",
  },
];

async function loadModules() {
  try {
    const data = await fetchJson("/user/literacy/modules");
    return data.modules;
  } catch {
    try {
      const data = await fetchJson("/literacy/modules");
      return data.modules;
    } catch {
      return FALLBACK_MODULES;
    }
  }
}

document.getElementById("nav").innerHTML = renderNav("learn");

requireOnboarding().then(async (profile) => {
  if (!profile) return;
  try {
    const modules = await loadModules();
    let profileData = profile;
    try {
      profileData = await fetchJson("/user/profile");
    } catch {
      /* use cached profile */
    }
    const done = new Set(profileData.literacy_completed || []);
    const list = document.getElementById("module-list");
    list.innerHTML = modules
      .map(
        (m) => `
      <article class="card lesson-card" data-id="${m.id}">
        <div class="lesson-head">
          <h2>${m.order}. ${m.title}</h2>
          ${done.has(m.id) ? '<span class="badge">Understood</span>' : ""}
        </div>
        <p class="muted">${m.summary}</p>
        <div class="lesson-body hidden">${(m.body || "").replace(/\n/g, "<br>")}</div>
        <p class="key-point hidden"><strong>Remember:</strong> ${m.key_point}</p>
        <button type="button" class="btn btn-secondary expand-btn">Read lesson</button>
        <button type="button" class="btn mark-done hidden">I understand — mark read</button>
      </article>`
      )
      .join("");

    list.querySelectorAll(".lesson-card").forEach((card) => {
      const expandBtn = card.querySelector(".expand-btn");
      const markBtn = card.querySelector(".mark-done");
      expandBtn.onclick = () => {
        card.querySelector(".lesson-body").classList.toggle("hidden");
        card.querySelector(".key-point").classList.toggle("hidden");
        markBtn.classList.toggle("hidden");
        expandBtn.textContent = card.querySelector(".lesson-body").classList.contains("hidden")
          ? "Read lesson"
          : "Hide";
      };
      markBtn.onclick = async () => {
        try {
          await fetchJson("/user/literacy/progress", {
            method: "POST",
            body: JSON.stringify({ module_id: card.dataset.id, completed: true }),
          });
        } catch {
          /* offline mark ok */
        }
        if (!card.querySelector(".badge")) {
          card.querySelector(".lesson-head").insertAdjacentHTML("beforeend", '<span class="badge">Understood</span>');
        }
      };
    });
  } catch (e) {
    document.getElementById("error").textContent =
      "Could not load lessons. Restart the server with: python run_mechanical.py";
  }
});
