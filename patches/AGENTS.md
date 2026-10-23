# patches — agent behaviour

## Reasoning

Patch the smallest upstream break. Do not hide a product rule inside a patch.

## WAT

- **Workflows:** apply on import from `financial_swarm.py`.
- **Agents:** none.
- **Tools:** the patch modules in this folder.

## Execution rules

If an upstream merge fights a patch, keep the start check (root `AGENTS.md`) red until it is reconciled. Do not fork product logic into a patch.
