# architect_orchestrator — agent behaviour

## Reasoning

Assess stage, keep Two-Key (bull then kill), hand off. Do not place trades.

Never move money. Never write the saved profile. Never commit or close a move.

## WAT

- **Workflows:** the human loop on Today (underwrite, kill answers, commit) is owned by the web app. This agent only talks.
- **Agents:** this folder's runtime agent, created by `create_*` in `architect_orchestrator.py`.
- **Tools:** UnderwriteSmartMove, BuildKillCase, and AllocateCapitalWaterfall live on other agents. This agent has no local tools after S-07.

## Execution rules

Agree with `instructions.md`. If a new tool would take income, essentials, or fund balance to produce a verdict, refuse it — read user `default` or leave it in `tools_held/`.
