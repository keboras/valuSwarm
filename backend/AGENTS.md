# backend — agent behaviour

## Reasoning

Saved state is the source. Preview then confirm. Grades travel with figures. COMPLETE is not FACT.

## WAT

- **Workflows:** covered writes listed in `../tests/covered_writes.md`; underwrite → kill answers → commit → journal.
- **Agents:** none live in this folder. HTTP routes serve the human and the optional advisor.
- **Tools:** `services/omni_wealth.py`, `services/profile_access.py` (load user `default`). Agent tools call these; they do not reimplement verdicts.

## Execution rules

- Covered figure writes return a diff when `confirm` is false.
- `two_key_complete` and `stability_fund_untouched` are computed, never literals.
- Tests must not use the live database.
