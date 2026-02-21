# CHECKPOINTS

## [GATE-0] Boot

### feature implemented
- `pnpm dev` orquestra gateway e web no monorepo
- Gateway em `http://localhost:3333`
- Web em `http://localhost:5173`
- `GET /health` responde `{ "ok": true }`
- `/login` renderiza como primeira tela para não autenticados

### regressions/errors
- Divergência anterior de portas (`3001/3000`) encontrada

### fixes/tests
- Ajustado para `3333/5173`
- Teste manual esperado:
  - `pnpm health`
  - abrir `http://localhost:5173/login`

---

## [GATE-1] Auth

### feature implemented
- Tabela `users` com `username`, `password_hash`, `role`
- Endpoints:
  - `POST /auth/login`
  - `POST /auth/logout`
  - `GET /auth/me`
- JWT em cookie `httpOnly`
- Rotas protegidas no web

### regressions/errors
- Nenhuma regressão funcional conhecida no scaffold

### fixes/tests
- `pnpm db:seed` cria `admin/admin123!`
- Teste manual esperado:
  - login válido retorna usuário
  - login inválido retorna 401
  - logout remove sessão

---

## [GATE-2] RBAC

### feature implemented
- Roles: `admin`, `operator`, `viewer`
- Middleware/permissões no gateway
- Route guards no web

### regressions/errors
- Nenhuma

### fixes/tests
- Teste manual esperado:
  - `viewer` não acessa `/admin/*`
  - `operator` acessa integrações, não usuários
  - `admin` acessa tudo

---

## [GATE-3] Admin UI

### feature implemented
- `/admin/users` (create user, reset password, assign role)
- `/admin/integrations` (CRUD + botão de teste)
- Tipos de integração: `http | mcp | cli`
- Persistência em SQLite com `secret_ref` (sem plaintext secret)

### regressions/errors
- Nenhuma

### fixes/tests
- Teste manual esperado:
  - criar usuário
  - alterar role
  - resetar senha
  - criar integração e testar conectividade

---

## [GATE-4] Jobs registry

### feature implemented
- Tabelas `jobs`, `job_events`, `artifacts`
- Endpoints:
  - `GET /api/jobs`
  - `POST /api/jobs`
  - `GET /api/jobs/:id`
  - `GET /api/jobs/:id/events`
- Artefatos em `./data/artifacts/<jobId>/`

### regressions/errors
- Nenhuma

### fixes/tests
- Teste manual esperado:
  - criar job no dashboard
  - listar jobs
  - consultar eventos por job

