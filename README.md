# MOI Investing Database — Public Docs

Public documentation site for the MOI Global Investing Database API.

**Live site:** https://docs.capmine.com/

## What is this repo?

This repository publishes a **sanitized public reference** for the `resolve-name` API. It is a mirror, not the source of truth. The source is a private repo held by MOI Global.

Machine-readable artifacts:

- `openapi.json` — OpenAPI 3.1 spec of the public API surface
- `status.json` — live coverage counts fetched from the production stats endpoint

## How is it kept in sync?

A GitHub Action (`.github/workflows/regenerate.yml`) runs:

- **Nightly at 03:00 UTC** (cron)
- **On every push to `main`**
- **On manual dispatch** (Actions tab -> Regenerate docs -> Run workflow)

The workflow calls the public `/stats` endpoint on the production API, then re-renders `index.html`, `openapi.json`, and `status.json` from the templates in `templates/`. If any output changed, it commits the diff back to `main`. GitHub Pages then redeploys automatically.

No secrets are required. The stats endpoint is public and returns aggregate counts only.

## Local development

```bash
python3 scripts/generate.py
```

Regenerates `index.html`, `openapi.json`, and `status.json` in place.

## License

Docs content: property of MOI Global. Anyone with a valid API key may use the endpoint described.
