---
name: canonical-parser-db
description: Implements and maintains the Canonical SSOT parser/validator pipeline (DSL -> normalized JSON -> schema validation -> SQL model) with idempotent event semantics. Use when tasks involve canonical payload parsing, schema evolution, Postgres migration updates, idempotency checks, or CI validation for canonical contracts.
---

# Canonical Parser + DB

## When to use
- User requests parser/validator changes for the canonical framework.
- User requests DB schema/migration updates for canonical context, IAM, or event log.
- User requests idempotency/atomicity checks around canonical payload persistence.
- User requests CI gates for canonical contract validation.

## Workflow
1. Validate or update `docs/canonical-dsl.v1.md` and `schema/canonical-normalized.v1.schema.json`.
2. Implement parser/normalizer rules in TypeScript (strict formats + invariants).
3. Ensure idempotency key remains deterministic (`sha256(normalized_json + schema_version)`).
4. Update SQL migration for `Core + Event Log` model.
5. Add/update tests for parse, validation, IAM catalog, idempotency, concurrency.
6. Ensure CI workflow blocks invalid canonical payloads.

## Required files (pilot reference)
- `pilot/canonical-ssot-v1/docs/canonical-dsl.v1.md`
- `pilot/canonical-ssot-v1/schema/canonical-normalized.v1.schema.json`
- `pilot/canonical-ssot-v1/src/canonical/*.ts`
- `pilot/canonical-ssot-v1/sql/0001_canonical_core_event_log.sql`
- `pilot/canonical-ssot-v1/tests/*.test.ts`
- `.github/workflows/canonical-validate.yml`

## Commands
```bash
cd pilot/canonical-ssot-v1
npm run build:types
./canonical parse --in examples/sample-complete.dsl --out artifacts/sample.json
./canonical validate --in artifacts/sample.json --schema schema/canonical-normalized.v1.schema.json
npm run validate:sql
npm test
```

## Quality bar
- No parser rule without test.
- No schema change without regenerated TS types.
- No migration change without SQL validation.
- Keep backward-compatible semantics unless operator explicitly authorizes breaking change.
