# Monorepo MVP (local-first)

Este arquivo resume o uso local do MVP. A versão principal está em `README.md`.

## Start rápido

```bash
pnpm install
pnpm db:seed
pnpm dev
```

- Gateway: `http://localhost:3333`
- Web: `http://localhost:5173`
- Login: `admin` / `admin123!`

## Escopo

- Sem Docker obrigatório para desenvolvimento local
- Sem Traefik/Portainer nesta fase
- Persistência local em `./data/app.db`

## Checkpoints

Acompanhe os gates em `docs/CHECKPOINTS.md`.
