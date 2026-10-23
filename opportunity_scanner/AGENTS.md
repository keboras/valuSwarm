# opportunity_scanner — agent behaviour

## Reasoning

Typed income is forbidden. Call UnderwriteSmartMove, which reads user default.

Never move money. Never write the saved profile. Never commit or close a move.

## WAT

- **Workflows:** the human loop on Today (underwrite, kill answers, commit) is owned by the web app. This agent only talks.
- **Agents:** this folder's runtime agent, created by `create_*` in `opportunity_scanner.py`.
- **Tools:** UnderwriteSmartMove (reads saved state). Other scanners stay in tools_held.

## Execution rules

Agree with `instructions.md`. If a new tool would take income, essentials, or fund balance to produce a verdict, refuse it — read user `default` or leave it in `tools_held/`.
