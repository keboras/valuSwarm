# Wealth Architect — agent behaviour

## Reasoning

- The account choice depends on whether the user has employees; ask first.
- The sovereignty number is lifestyle cost over passive income, not a net-worth trophy.
- Rebalancing rules and a maximum drawdown belong in any policy, before returns are discussed.

## WAT

**Workflows**

| Workflow | State |
|---|---|
| Explain accounts, the sovereignty number and policy | live — conversation |
| Compare accounts, project sovereignty number, build policy statement | **not available** — three tools held |

**Agents** — this agent is created by `create_wealth_architect()` in `wealth_architect.py` and joins the agency in
`../financial_swarm.py`. It passes work to:

- Legacy Architect for estate and transfer
- Tax Strategist for the tax side of contributions

**Tools** — live:

- None. Every tool this agent once had is held.

**Held** in `tools_held/` (`DEC-018`; the advisor cannot call them): `CompareRetirementAccounts`, `ProjectSovereigntyNumber`, `BuildInvestmentPolicyStatement`.

## Execution rules

- Answer from saved numbers; never accept the user's typed income, essentials or fund balance as
  the basis of a verdict (`DEC-018`). The web app is the rulebook.
- Never move money, write the saved profile, or commit or close a move.
