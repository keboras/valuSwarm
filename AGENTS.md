# valuSwarm — agent behaviour

## Binding decisions

Source: `C:\Users\kebor\Projects\Agentic WorkFlow\clients\agentic-workflow\systems\valuswarm\decision_register.md`

- `DEC-001` KEEP list (evidence labels, completeness distinct from a total, Level 4 human money-movement boundary, deterministic calculation, FACT update path)
- `DEC-002` (COMPLETE is not known; verified only for FACT)
- `DEC-007` (opportunity-cost comparison on a deployment-shaped move — still open whether valuSwarm packets must add it)
- `DEC-008` (proof by fixture, never a live deal)
- `DEC-014` valuSwarm is the product home
- `DEC-015` this PC, one user, no accounts
- `DEC-016` bind loopback only
- `DEC-017` financial data never in git
- `DEC-018` advisor is optional; one rulebook on saved state
- `DEC-019` ICM operating spine
- `DEC-020` Two-Key, kill answers, journal
- `DEC-021` cheap upstream merges; start check before merge
- `DEC-022` Command Center carries console gates
- `DEC-023` Today is home
- `DEC-024` governed folders (this spine)
- `DEC-025` `.cursor/rules/agency-swarm-workflow.mdc` is `alwaysApply: false`

## Daily start (S-01)

From a fresh Windows terminal in this repository:

```text
start.bat
```

That runs `python run_mechanical.py`. No model key is required. Open `http://localhost:8090/`. Health: `GET /health/mechanical`.

Full advisor (optional): `python server.py` after a model key is set. If the advisor fails to load, the web app still starts.

## Start check before any upstream merge (S-03)

```text
python -c "from financial_swarm import create_agency; from backend.app import create_mechanical_app; create_mechanical_app(); create_agency()"
```

This must import and build the agency without calling a model. If it raises, do not merge upstream.

## Reasoning

- Responsibility before mechanism. Saved state is the only figure source for verdicts, allocation, and net worth.
- A preview that was not confirmed did not happen.
- COMPLETE means the schema has values. It does not mean the figures are known.
- The advisor never writes the profile, never commits, never closes a move, and never computes a verdict from typed income.

## WAT

- **Workflows:** intake (onboarding), Today (route money, mark done), underwrite → kill answers → commit → journal, weekly review. Repeatable steps live in the UI and `backend/services/omni_wealth.py`, not in this file.
- **Agents:** the 15 financial agents in this repo, plus optional Studio specialists. They reason and route. They do not move money.
- **Tools:** only `UnderwriteSmartMove`, `BuildKillCase`, and `AllocateCapitalWaterfall` are available to the advisor. They read user `default` through the service layer. Other tool files are in `tools_held/`. Classification: `backend/advisor_tool_classification.md`.

## Execution rules

- Bind `127.0.0.1` only.
- Never commit `*.db`, uploads, or vault files.
- Tests must use a throwaway database (`tests/conftest.py`).
- Do not copy Capability Packs into this spine. Point at them.
