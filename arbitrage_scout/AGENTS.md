# Arbitrage Scout — agent behaviour

## Reasoning

- Prefer gains realisable within 30 days; slow arbitrage is just investing.
- A recurring saving is worth more than a one-off gap of the same size.
- Switch friction (contracts, setup time) is part of the cost.

## WAT

**Workflows**

| Workflow | State |
|---|---|
| Talk through a vendor saving or pricing gap | live — conversation with web sources |
| Score opportunity velocity, scan vendor pricing, track pipeline | **not available** — three tools held |

**Agents** — this agent is created by `create_arbitrage_scout()` in `arbitrage_scout.py` and joins the agency in
`../financial_swarm.py`. It passes work to:

- Opportunity Scanner for any concrete bet
- Architect Orchestrator when the stage gate refuses

**Tools** — live:

- None. Every tool this agent once had is held.

**Held** in `tools_held/` (`DEC-018`; the advisor cannot call them): `ScoreOpportunityVelocity`, `ScanVendorPricingArbitrage`, `TrackArbitragePipeline`.

## Execution rules

- Answer from saved numbers; never accept the user's typed income, essentials or fund balance as
  the basis of a verdict (`DEC-018`). The web app is the rulebook.
- Never move money, write the saved profile, or commit or close a move.
