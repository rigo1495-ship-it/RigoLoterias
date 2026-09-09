# Phase J2 — production configuration and first staging deployment

J2 validates Render using only its temporary `onrender.com` hostnames. Do not configure Cloudflare or a custom domain yet.

## Render values (outside Git)

When importing the Blueprint, set these values in Render:

| Variable | Service | Staging value |
| --- | --- | --- |
| `CORS_ORIGINS` | API | Exact static-site URL, `https://<web-host>.onrender.com` |
| `TRUSTED_HOSTS` | API | Exact API hostname, `<api-host>.onrender.com` |
| `VITE_API_BASE_URL` | static web | `https://<api-host>.onrender.com/api/v1` |
| `WRITE_API_TOKEN` | API | Render-generated; retain only in administrative secret storage |
| `DATABASE_URL` | API | Injected internally by `fromDatabase`; do not manually paste it |

The PostgreSQL plan in `render.yaml` is paid and supports the production recovery path; it is not a substitute for the external backups and restore drill planned for J4.

## Deploy and validate

1. Import `render.yaml` as a Render Blueprint, supply the prompted values, and wait for the API pre-deploy migration and `/api/v1/ready` health check to pass.
2. Confirm the exact API and static-site URLs in Render. If a prompted URL differs, update that environment variable in Render and redeploy the affected service.
3. Run the smoke test from a secure administrative environment. Do not put its token in command history:

```bash
export WRITE_API_TOKEN='value-from-secret-manager'
python scripts/smoke_staging.py \
  --api-url 'https://<api-host>.onrender.com/api/v1' \
  --frontend-url 'https://<web-host>.onrender.com'
unset WRITE_API_TOKEN
```

The smoke test verifies health/readiness, all eight available games, valid and invalid CORS, invalid Host, import authorization, request IDs and absence of the write token from served frontend assets. It uses an import preview only and never persists a draw.

## 500 response check

The generic 500 response is covered by application tests. Do not manufacture production failures merely to test it. Verify it during J5 with a controlled staging fault while retaining the returned `X-Request-ID` for log correlation.

## J2 completion gate

Record the API/static URLs, Render deployment IDs, migration result and smoke-test output in the deployment record. J2 is complete only when the script passes against staging and no secret appears in Render logs, responses or the frontend bundle.
