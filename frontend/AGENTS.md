# frontend — agent behaviour

## Reasoning

Show the change, then ask. Never display a traceback or a raw file path.

## WAT

- **Workflows:** route money → mark done; underwrite → answer kill reasons → commit; weekly review.
- **Agents:** none. The browser is the human surface.
- **Tools:** `js/home.js`, `js/onboarding.js`, `js/app.js` talking to `/wealth` and `/user`.

## Execution rules

Covered writes send a preview (`confirm: false` or no confirm) then a confirming request. Advisor status copy is the phrase advisor unavailable when the side panel cannot load.
