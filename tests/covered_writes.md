# Covered writes (S-11)

Every request in `backend/routers` that changes a saved financial figure must first return a diff and write only on `confirm=true` (query) or `confirm: true` (body). Goals (North Star) are not figures.

| Route | Covered? | Why |
|---|---|---|
| `POST /wealth/state` | yes | Saves cash, accounts, assets, investments, loans |
| `POST /wealth/inflow/done` | yes | Adds to Stability Fund or investments |
| `POST /user/onboarding` | yes | Saves income, essentials, fund balance |
| `POST /user/intake/step/{step}` | yes | Saves intake figures including debt |
| `POST /user/intake/complete` | yes | Marks intake complete on those figures |
| `POST /user/intake/reset` | yes | Deletes the profile |
| `POST /user/contract/sign` | yes | Derives profile figures from the audit |
| `PATCH /user/profile` | yes | Can change income, essentials, fund |
| `POST /wealth/north-star` | no | Goal, not a figure |
| `POST /wealth/inflow` | no | Stores a routing plan; balances change only on mark-done |
| `POST /wealth/moves/underwrite` | no | Stores a packet, not a figure |
| `POST /wealth/moves/commit` | no | Journal + move status; no figure write |
| `POST /wealth/moves/close` | no | Result text, not a balance |
| `POST /wealth/reinvest/compare` | no | Read-only comparison |
| `POST /user/literacy/progress` | no | Lesson ids, not money |
| `POST /user/footprints/connect` | no | Flags for bank/calendar/screen |
| `POST /user/clinical-audit/acknowledge` | no | Pattern ids |
| `POST /user/focus-season` | no | UI mode and hour |
| `POST /mirror/*` | no | Pause items, not saved figures |
| `POST /reputation/*` | no | Commitments and scores, not balances |
| `PUT/DELETE /user/memory/*` | no | Chat and facts |
| `POST /studio/*` | no | Generated files |
