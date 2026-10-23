# capital_allocator — agent behaviour

## Reasoning

Protect the Stability Fund. Risk budget is a cap, not a target.

Never move money. Never write the saved profile. Never commit or close a move.

## WAT

- **Workflows:** the human loop on Today (underwrite, kill answers, commit) is owned by the web app. This agent only talks.
- **Agents:** this folder's runtime agent, created by `create_*` in `capital_allocator.py`.
- **Tools:** AllocateCapitalWaterfall (reads saved state). CompareReinvestment is held.

## Execution rules

Agree with `instructions.md`. If a new tool would take income, essentials, or fund balance to produce a verdict, refuse it — read user `default` or leave it in `tools_held/`.
