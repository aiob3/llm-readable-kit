# WORKFLOW

Este documento segmenta pedidos do operador e organiza homologação por gate.

## new_features

- Scaffold local-first monorepo com `pnpm` + `turbo`
- `apps/gateway` (Node 20 + Fastify + TS + SQLite)
- `apps/web` (Vite + React + TS)
- Migrações SQL idempotentes em `apps/gateway/migrations/*.sql`
- Scripts raiz: `dev`, `db:reset`, `db:seed`, `health`

## scope_extra

- Contexto de autenticação no frontend
- Guards de role (`admin`, `operator`, `viewer`)
- CRUD-lite de usuários e integrações
- Registro básico de jobs/eventos/artefatos

## homologation

Formato obrigatório: **Function > Features(by milestone) > Interfaces > Content**

### Function
- Gateway API + Web App

### Features(by milestone)
- Gate 0: Boot
- Gate 1: Auth
- Gate 2: RBAC
- Gate 3: Admin UI
- Gate 4: Jobs registry

### Interfaces
- HTTP REST (`/health`, `/auth/*`, `/admin/*`, `/api/jobs*`)
- UI (`/login`, `/`, `/admin/users`, `/admin/integrations`)

### Content
- SQLite em `./data/app.db`
- Artefatos em `./data/artifacts/<jobId>/`
- Sem armazenamento de segredo em plaintext (usar `secret_ref`)

## feedback

### errors/bug/fix/test
- Registrar regressão por gate em `docs/CHECKPOINTS.md`
- Registrar correção aplicada
- Registrar teste executado e resultado

### roadmap/backlog/pendencias
- Itens não-MVP ficam em backlog
- Não bloquear homologação dos gates atuais

