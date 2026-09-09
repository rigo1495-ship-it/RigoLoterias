# Hardening baseline

RigoLoterias is an analysis platform, not a betting or payment service. It does not store payment data or place wagers.

## Configuration

Copy `.env.example` to `.env`; do not commit `.env`. Set `DATABASE_URL` to the deployment database and set `CORS_ORIGINS` and `TRUSTED_HOSTS` to exact comma-separated deployed origins/hosts. Never use `*` for a deployed environment.

`ENVIRONMENT` accepts `development`, `test` or `production`. Deploy behind TLS termination and run database migrations before serving traffic.

## API baseline

The API sends `nosniff`, frame-denial, no-referrer and same-site resource headers. CORS allows only configured origins, unapproved Host headers are rejected, public methods are limited to GET/POST/OPTIONS, and response compression is enabled for substantial payloads. Database connection checkout uses pre-ping.

`/api/v1/health` is a liveness probe; `/api/v1/ready` checks database connectivity and returns 503 on failure. The process-local sliding-window limiter uses the direct socket peer only, never client-supplied forwarding headers. Configure `RATE_LIMIT_REQUESTS` and `RATE_LIMIT_WINDOW_SECONDS` to the traffic budget. For multiple API instances, enforce the same policy at the load balancer/API gateway; the local limiter is intentionally a second line of defence, not distributed state.

Authentication, user accounts, payments and rate limiting are intentionally not implemented because the platform has no corresponding product flow. Add them only with a concrete authorization and threat model.
