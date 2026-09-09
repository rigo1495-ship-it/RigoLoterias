# Hardening baseline

RigoLoterias is an analysis platform, not a betting or payment service. It does not store payment data or place wagers.

## Configuration

Copy `.env.example` to `.env`; do not commit `.env`. Set `DATABASE_URL` to the deployment database and set `CORS_ORIGINS` to the exact comma-separated frontend origins. Never use `*` for a deployed environment.

`ENVIRONMENT` accepts `development`, `test` or `production`. Deploy behind TLS termination and run database migrations before serving traffic.

## API baseline

The API sends `nosniff`, frame-denial, no-referrer and same-site resource headers. CORS allows only configured origins, public methods are limited to GET/POST/OPTIONS, and response compression is enabled for substantial payloads. Database connection checkout uses pre-ping.

Authentication, user accounts, payments and rate limiting are intentionally not implemented because the platform has no corresponding product flow. Add them only with a concrete authorization and threat model.
