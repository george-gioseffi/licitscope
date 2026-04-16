# Security policy

LicitScope is a portfolio-grade open-source project. It does not process
real personal data and has no authentication surface in the MVP — but we
still take security posture seriously, both as a learning artefact and
out of respect for the public-data sources it consumes.

## Reporting a vulnerability

If you believe you've found a security issue in LicitScope:

1. **Do not open a public issue.**
2. Email the maintainer at the address published on the repo's
   [GitHub profile](https://github.com/george-gioseffi) with:
   - a clear description of the issue,
   - steps to reproduce,
   - the commit SHA or release tag you observed it on,
   - (optional) a suggested fix.

We will acknowledge receipt within 5 business days and follow up with a
plan. If you'd like to coordinate a public disclosure date after the fix
ships, say so in the report.

## Scope

This project is a portfolio MVP. The **in-scope** surface is:

- SQL/SSRF/SSRF-through-fixture paths in ingestion
- any flaw that lets a crafted PNCP payload corrupt stored data
- XSS or prototype pollution in the Next.js frontend
- dependency chain vulnerabilities surfaced by CodeQL / Dependabot

**Out of scope** for v0.x:

- authentication, authorization, multi-tenancy (not implemented)
- rate limiting (not implemented)
- anything that requires access to a non-public data source

## Security features already shipped

- CodeQL scan runs weekly over both Python and JavaScript surfaces.
- Dependabot is wired for pip, npm, and GitHub Actions.
- `npm ci` in CI enforces lockfile integrity.
- Pre-commit hook blocks files larger than 512 KB (leakage guard).
- All PNCP responses are fed through typed Pydantic validation before
  any mapping into the domain layer.
- Raw payloads are persisted keyed by SHA-256 content hash so integrity
  of any record can be re-verified.
