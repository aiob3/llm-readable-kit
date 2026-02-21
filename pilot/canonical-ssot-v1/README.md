# Canonical SSOT v1 Pilot (Web + Postgres)

Pilot implementation of the proprietary canonical framework with:
- DSL input (`canonical-dsl.v1`)
- deterministic JSON normalization (`canonical-normalized.v1`)
- idempotent event strategy (`sha256(normalized_json + schema_version)`)
- Postgres Core + Event Log model
- Next.js feature-driven reference UI

## Structure
- `docs/canonical-dsl.v1.md`: canonical DSL spec
- `schema/canonical-normalized.v1.schema.json`: JSON Schema contract
- `src/cli.ts`: parser/validator CLI
- `sql/0001_canonical_core_event_log.sql`: initial migration
- `app/` + `src/features/`: frontend reference
- `tests/`: parser/idempotency/frontend-validation tests

## CLI
```bash
./canonical parse --in examples/sample-complete.dsl --out artifacts/sample.json
./canonical validate --in artifacts/sample.json --schema schema/canonical-normalized.v1.schema.json
./canonical emit-sql --in artifacts/sample.json --out artifacts/0001_snapshot.sql
./canonical scaffold-frontend --in artifacts/sample.json --target /tmp/canonical-app
```

## Local setup
```bash
npm install
npm run build:types
npm run parse:sample
npm run validate:sample
npm test
npm run validate:sql
```

## Frontend
```bash
npm run dev
```

Routes:
- `POST /api/canonical/parse`: DSL -> normalized JSON
- `GET /api/canonical/events`: timeline (memory fallback)
- `POST /api/canonical/events`: persist event (Postgres first)

## Postgres
Set `DATABASE_URL` and apply migration:
```bash
psql "$DATABASE_URL" -f sql/0001_canonical_core_event_log.sql
```

## CI required check
Workflow: `.github/workflows/canonical-validate.yml`
Required status check name: `canonical-validate`.
