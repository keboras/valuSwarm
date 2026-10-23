# Root context — valuSwarm product

## Mission

Run OmniWealth on this PC for one user: honest figures, Today as home, Two-Key before a commit, human money movement.

## Operating context

Windows. Loopback only. SQLite file created on first start under `data/` (gitignored). Advisor is optional. Upstream OpenSwarm remains a fork parent.

## Success criteria

- `start.bat` brings up the web app with no model key
- Today can log an inflow, show each dollar's job, and mark it done
- Covered figure writes preview a diff and wait for confirm
- Advisor failure does not take the app down

## Constraints

- No accounts, no hosted access, no money movement by software
- Do not retune verdict thresholds
- Do not put balances, income figures, account identifiers or secrets in spine files
- Capability Packs stay outside this repo; reference them only
