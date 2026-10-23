# tests context

## Mission

Prove S-01–S-13 without touching Kevin's database.

## Operating context

`pytest.ini` sets `pythonpath = .`. Session fixture hashes the live db file.

## Success criteria

The suite passes on a throwaway SQLite file. The live db hash is unchanged.

## Constraints

No live-deal proof. Fixture user ids only.
