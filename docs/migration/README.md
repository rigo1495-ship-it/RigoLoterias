# Migration safety

TRIS MASTER, GatoSolver, MELATE CONTROL, Protouch Analytics, PROGOL RIGO ELITE and Registro
Local are read-only references.

- Never run canonical Alembic migrations against their SQLite databases.
- Never modify original historical files.
- Copy data only after explicit authorization.
- Record source hashes, parser versions, accepted rows and rejected rows.
- Validate adapted behavior with source-versus-target golden tests.

Phase A performs no source-code or data migration.

