# Phase J1 — Render deployment foundation

This blueprint provisions a Render Python API, a static Vite frontend and managed PostgreSQL. It does not deploy a domain, Cloudflare configuration, backups or monitoring; those belong to J2–J5.

## Before creating the Blueprint

1. Push this repository and create a Blueprint from `render.yaml`.
2. At the Render prompts, provide only real production values, never source-controlled values:
   - `CORS_ORIGINS`: the exact frontend URL, for example the assigned Render static-site URL.
   - `TRUSTED_HOSTS`: the exact Render API hostname. Add the custom API domain later in J2.
   - `VITE_API_BASE_URL`: the full public API prefix, such as `https://<api-host>/api/v1`.
3. Render generates `WRITE_API_TOKEN`; copy it only to the approved administrative import client. It must never be placed in the frontend, Git, browser storage or logs.

The PostgreSQL connection is wired internally through Render's `fromDatabase` reference. It is not present in Git. The API runs `alembic upgrade head` as its pre-deploy step and accepts traffic only after `/api/v1/ready` confirms database connectivity.

## Deploy order and smoke checks

After the first API deployment, confirm the generated API hostname and update the static site's `VITE_API_BASE_URL` if necessary, then redeploy the static site. Verify:

```text
GET  https://<api-host>/api/v1/health  -> 200
GET  https://<api-host>/api/v1/ready   -> 200
GET  https://<api-host>/api/v1/games   -> 200, eight games
```

From the configured frontend origin, CORS must allow API reads. A different origin and an invalid Host must not be accepted. `POST .../imports` must fail without `X-API-Key` and succeed only with the generated server-side token.

## Notes

The blueprint uses paid plans because the pre-deploy migration step and production persistence are intentional production requirements. Keep the API and database in the same region. Before public traffic, complete J2 (Cloudflare/TLS), J3 (external backups), J4 (alerts) and J5 (restore drill).

Render source references: [Blueprint specification](https://render.com/docs/blueprint-spec), [health checks](https://render.com/docs/health-checks), [monorepo support](https://render.com/docs/monorepo-support).
