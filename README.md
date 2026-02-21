# Local-first Monorepo MVP

Monorepo com `pnpm workspaces` + `Turborepo`:

- `apps/gateway` → Node 20 + Fastify + TypeScript
- `apps/web` → Vite + React + TypeScript
- SQLite local em `./data/app.db`

## Requisitos

- Node.js 20+
- pnpm 8+

## Passos locais (exatos)

```bash
pnpm install
pnpm db:seed
pnpm dev
```

Depois abra:

- Gateway: `http://localhost:3333`
- Web: `http://localhost:5173`

Login inicial:

- usuário: `admin`
- senha: `admin123!`

> Observação: o login é com `username=admin` e `password=admin123!`.

## Scripts

- `pnpm dev` → sobe gateway + web
- `pnpm db:reset` → remove `./data/app.db` e `./data/artifacts`
- `pnpm db:seed` → cria usuário admin inicial
- `pnpm health` → verifica `GET /health`

## Gates implementados

- Gate 0 — Boot
  - gateway em `:3333`, web em `:5173`, `/health` retorna ok, `/login` renderiza
- Gate 1 — Auth
  - `/auth/login`, `/auth/logout`, `/auth/me` + cookie `httpOnly` JWT
- Gate 2 — RBAC
  - roles `admin/operator/viewer` no gateway e guards no web
- Gate 3 — Admin UI
  - `/admin/users` (create/reset password/assign role)
  - `/admin/integrations` (CRUD + test)
- Gate 4 — Jobs registry
  - `/api/jobs`, `/api/jobs/:id`, `/api/jobs/:id/events`
  - artefatos em `./data/artifacts/<jobId>/`

## Migrations

- SQL em `apps/gateway/migrations/*.sql`
- Runner idempotente aplica cada arquivo uma única vez
- Tabela `migrations` rastreia arquivos aplicados

## Variáveis de ambiente

Use `.env` local baseado em `.env.example`:

```env
DATA_DIR=./data
JWT_SECRET=dev-secret
COOKIE_SECURE=false
```

## VPS packaging later

Empacotamento para VPS será adicionado depois (artefatos de deploy). Este MVP é intencionalmente local-first e sem arquivos de Traefik/Portainer neste momento.
