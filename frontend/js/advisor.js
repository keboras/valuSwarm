import { fetchJson, requireOnboarding, renderNav } from "./app.js";

const AGENCY_PATH = "/Architect_Blueprint/get_response";
const STARTERS = [
  "Build my debt payoff order",
  "How much should I set aside for taxes?",
  "Am I ready for a business line of credit?",
  "What's my next Stability-stage move?",
];

let financialSummary = null;
let chatHistory = [];

function appendMessage(role, text) {
  const log = document.getElementById("chat-log");
  const div = document.createElement("div");
  div.className = role === "user" ? "chat-user" : "chat-assistant";
  div.textContent = text;
  log.appendChild(div);
  log.scrollTop = log.scrollHeight;
}

async function checkAdvisorAvailable() {
  try {
    const res = await fetch(`${AGENCY_PATH.replace("/get_response", "/get_metadata")}`);
    return res.ok;
  } catch {
    return false;
  }
}

async function sendMessage(text) {
  appendMessage("user", text);
  document.getElementById("chat-input").value = "";

  const contextBlock = financialSummary
    ? `User financial profile (use these numbers):\n${JSON.stringify(financialSummary, null, 2)}`
    : "No financial profile loaded.";

  const res = await fetch(AGENCY_PATH, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message: text,
      recipient_agent: "Architect Orchestrator",
      additional_instructions: contextBlock,
      user_context: { financial_summary: financialSummary },
      chat_history: chatHistory.length ? chatHistory : null,
    }),
  });

  if (!res.ok) {
    const err = await res.text();
    appendMessage("assistant", `Advisor unavailable: ${err}. Run full server: python server.py (not run_mechanical.py only).`);
    return;
  }

  const data = await res.json();
  const reply = data.response || data.final_output || data.message || JSON.stringify(data);
  appendMessage("assistant", String(reply));
  if (data.chat_history) chatHistory = data.chat_history;
}

document.getElementById("nav").innerHTML = renderNav("advisor");

requireOnboarding().then(async () => {
  const statusEl = document.getElementById("advisor-status");
  const available = await checkAdvisorAvailable();
  if (!available) {
    statusEl.textContent =
      "AI advisor requires the full server. Run: python server.py (with OPENAI_API_KEY). Mechanical-only mode has no chat.";
    statusEl.classList.remove("hidden");
  }

  try {
    financialSummary = await fetchJson("/user/intake/summary");
    appendMessage(
      "assistant",
      `Profile loaded for ${financialSummary.display_name}. Income ${financialSummary.monthly_gross_income}, debt total ${financialSummary.debt_total}. Ask anything.`
    );
  } catch {
    appendMessage("assistant", "Complete Financial Reality Intake first for personalized answers.");
  }

  const chips = document.getElementById("starter-chips");
  chips.innerHTML = STARTERS.map(
    (s) => `<button type="button" class="btn btn-secondary btn-sm starter">${s}</button>`
  ).join("");
  chips.querySelectorAll(".starter").forEach((btn) => {
    btn.onclick = () => sendMessage(btn.textContent);
  });

  document.getElementById("chat-form").onsubmit = (e) => {
    e.preventDefault();
    const text = document.getElementById("chat-input").value.trim();
    if (text) sendMessage(text);
  };
});
