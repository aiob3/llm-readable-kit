# Schema Postgres Canônico — Memora Pilot

## canonical_context
```sql
CREATE TABLE canonical_context (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id  TEXT NOT NULL,
  project     TEXT,
  user_id     TEXT,
  metadata    JSONB,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);
```

## canonical_identity
```sql
CREATE TABLE canonical_identity (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name        TEXT NOT NULL,
  type        TEXT,  -- 'person' | 'system' | 'org'
  attributes  JSONB,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);
```

## canonical_event_log (append-only — nunca UPDATE/DELETE)
```sql
CREATE TABLE canonical_event_log (
  id          BIGSERIAL PRIMARY KEY,
  event_type  TEXT NOT NULL,
  payload     JSONB NOT NULL,
  context_id  UUID REFERENCES canonical_context(id),
  identity_id UUID REFERENCES canonical_identity(id),
  zone        TEXT,  -- referência a canonical_zone_catalog
  created_at  TIMESTAMPTZ DEFAULT NOW()
);
```

## canonical_role_catalog
```sql
CREATE TABLE canonical_role_catalog (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name        TEXT UNIQUE NOT NULL,
  permissions JSONB
);
```

## canonical_zone_catalog
```sql
CREATE TABLE canonical_zone_catalog (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name        TEXT UNIQUE NOT NULL,
  description TEXT
);
```

## canonical_acl_binding
```sql
CREATE TABLE canonical_acl_binding (
  identity_id UUID REFERENCES canonical_identity(id),
  role_id     UUID REFERENCES canonical_role_catalog(id),
  zone_id     UUID REFERENCES canonical_zone_catalog(id),
  PRIMARY KEY (identity_id, role_id, zone_id)
);
```

## Conexão Postgres (Pool pattern)
```typescript
import { Pool } from 'pg';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: 10,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});
```
