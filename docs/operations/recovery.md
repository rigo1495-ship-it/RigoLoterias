# Backup and recovery

## SQLite local deployments

Create an atomic, integrity-checked snapshot without stopping the service:

```bash
python scripts/backup_sqlite.py backend/rigoloterias.sqlite3 /secure/backups/rigoloterias-$(date +%F).sqlite3
```

Store snapshots outside the repository and test restoration regularly. To restore, stop the API, retain the failed database as evidence, atomically replace it with a verified snapshot, run `backend/.venv/bin/alembic upgrade head`, then check `/api/v1/ready` before accepting traffic.

## PostgreSQL production deployments

Use managed point-in-time recovery or scheduled `pg_dump` backups encrypted at rest and retained outside the application host. Test restore into an isolated environment, run `alembic upgrade head`, and verify `/api/v1/ready`. Database credentials belong in deployment secret storage, never in the repository or frontend bundle.

## Failure signals

Use `/api/v1/health` for liveness and `/api/v1/ready` for database readiness. Correlate failures by `X-Request-ID`; logs intentionally exclude request bodies and query strings.
