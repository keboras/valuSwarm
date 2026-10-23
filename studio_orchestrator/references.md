# Studio Orchestrator — references

- `instructions.md` — runtime prompt (Process and Output Format sections are the source of this folder's workflows)
- `../frontend/studio.html` — the Studio screen this agent serves
- `../docs_agent/`, `../slides_agent/`, `../image_generation_agent/`, `../video_generation_agent/` — the specialists it routes to (upstream OpenSwarm agents, not governed here)
- `../backend/advisor_tool_classification.md` — which of this agent's tools are live and which held
- Decisions: `DEC-018` (agents are an optional advisor layer), `DEC-024` (this folder is governed) —
  `Agentic WorkFlow/clients/agentic-workflow/systems/valuswarm/decision_register.md`
