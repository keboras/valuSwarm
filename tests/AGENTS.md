# tests — agent behaviour

## Reasoning

A check that passes on the unmodified baseline was written wrongly if the spec said it must fail there.

## WAT

- **Workflows:** `pytest tests` from the repo root.
- **Agents:** the builder and reviewer run this folder; no runtime agent lives here.
- **Tools:** pytest, the mechanical FastAPI app, `conftest.py` throwaway database.

## Execution rules

`conftest.py` sets `DATABASE_URL` before imports. If a test asserted a defect this spec removes, list the change in the run notes.
