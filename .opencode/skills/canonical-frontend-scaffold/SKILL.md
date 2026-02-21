---
name: canonical-frontend-scaffold
description: Builds and evolves the Canonical SSOT frontend template (Next.js feature-driven) for DSL input, semantic review, IAM visualization, and canonical timeline. Use when tasks involve canonical UI flows, API integration, validation UX, or frontend scaffolding for new projects.
---

# Canonical Frontend Scaffold

## When to use
- User requests a new web interface based on Canonical SSOT.
- User requests changes in canonical UI flow (input/review/iam/timeline).
- User requests frontend-side validation/error mapping for canonical payloads.

## Workflow
1. Keep feature-driven structure:
   - `src/features/canonical-input`
   - `src/features/canonical-review`
   - `src/features/canonical-iam`
   - `src/features/canonical-timeline`
2. Keep schema-backed types in `src/shared/schema/generated-types.ts`.
3. Keep validation mapping in `src/shared/validation/error-map.ts`.
4. Expose API routes for parse and persistence integration.
5. Add UI and behavior tests when UX validation rules change.

## Required files (pilot reference)
- `pilot/canonical-ssot-v1/app/page.tsx`
- `pilot/canonical-ssot-v1/app/api/canonical/parse/route.ts`
- `pilot/canonical-ssot-v1/app/api/canonical/events/route.ts`
- `pilot/canonical-ssot-v1/src/features/**`
- `pilot/canonical-ssot-v1/src/shared/**`

## Commands
```bash
cd pilot/canonical-ssot-v1
npm run dev
npm test
```

## Quality bar
- Preserve deterministic semantics between UI and parser.
- Errors must map to canonical error classes (`E_PARSE_*`, `E_SCHEMA_*`, `E_IAM_*`, `E_IDEMPOTENCY_*`).
- Mobile and desktop layouts must remain usable.
