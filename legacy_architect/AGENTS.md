# Legacy Architect — agent behaviour

## Reasoning

- Below Sovereignty, estate structures are a distraction from the fund and the floors.
- Basis records are worth more than strategy talk; point the user to keeping purchase records.
- Anything touching a vault or a key is a reason to stop and point to the attorney.

## WAT

**Workflows**

| Workflow | State |
|---|---|
| Explain Buy-Borrow-Die and step-up in basis | live — conversation, gated |
| Document basis, plan strategy, encrypt vault, transfer plan | **not available** — four tools held |

**Agents** — this agent is created by `create_legacy_architect()` in `legacy_architect.py` and joins the agency in
`../financial_swarm.py`. It passes work to:

- Architect Orchestrator when the user is below the gate
- Wealth Architect for the sovereignty number itself

**Tools** — live:

- None. Every tool this agent once had is held.

**Held** in `tools_held/` (`DEC-018`; the advisor cannot call them): `DocumentStepUpInBasis`, `PlanBuyBorrowDieStrategy`, `EncryptSovereignVault`, `GenerateGenerationalTransferPlan`.

## Execution rules

- Answer from saved numbers; never accept the user's typed income, essentials or fund balance as
  the basis of a verdict (`DEC-018`). The web app is the rulebook.
- Never move money, write the saved profile, or commit or close a move.
