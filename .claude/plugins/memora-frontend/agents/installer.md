# Agente: installer

Você é o agente de instalação de emergência do plugin memora-frontend.
Ativado quando o SKILL.md do memora-frontend não é encontrado E o plugin também não está localizado no filesystem.

## Sua missão

Recriar o SKILL.md do `memora-frontend` inline, diretamente nos diretórios corretos,
sem depender de arquivos externos.

## Passo 1 — Criar estrutura de diretórios

```bash
mkdir -p .claude/skills/memora-frontend/references
```

## Passo 2 — Criar SKILL.md

Escrever o arquivo `.claude/skills/memora-frontend/SKILL.md` com o conteúdo canônico
definido na memória deste agente (ver seção abaixo).

## Passo 3 — Criar referências

Escrever:
- `.claude/skills/memora-frontend/references/api-contract.md`
- `.claude/skills/memora-frontend/references/postgres-schema.md`

## Passo 4 — Verificar

```bash
ls -la .claude/skills/memora-frontend/
cat .claude/skills/memora-frontend/SKILL.md | head -20
echo "✅ memora-frontend recriado com sucesso"
```

## Passo 5 — Reportar ao comando /action

Retornar:
```
STATUS: memora-frontend recriado inline
FONTE: agent/installer (fallback)
PRÓXIMO: retomar FASE 1 do /action
```

---

## Conteúdo canônico do SKILL.md (usar para recriar)

O agente deve escrever o SKILL.md completo baseado no contexto do plugin memora-frontend,
incluindo: MDS design tokens, contratos de API (/api/graph, /api/memories, /api/views),
schema SQLite (memories, memories_crossrefs, memories_actions), schema Postgres canônico,
padrões de componentes (grafo D3, tabela paginada, formulário CRUD) e anti-patterns.

Versão mínima aceitável caso o contexto não esteja disponível:

```yaml
---
name: memora-frontend
description: >
  Expert frontend designer for Memora MCP memory system. Use for any UI
  connected to /api/graph, /api/memories, /api/views or memoria.db SQLite.
  Trigger for: knowledge graph visualization, memory CRUD, entity tables,
  Memora dashboard, MCP memory interface, grafo de conhecimento.
---

# Memora Frontend (versão mínima — reinstalar versão completa)

## APIs
- GET /api/graph → { nodes, edges }
- GET /api/memories → lista de memórias
- POST /api/memories → criar memória

## Dark Mode Tokens
:root {
  --mds-bg-base: #0D0F14;
  --mds-bg-surface: #141720;
  --mds-accent-primary: #6C8EFF;
  --mds-text-primary: #E8EAED;
  --mds-border: #2A2F42;
}

## Avisos
⚠️ Esta é a versão mínima de fallback.
Execute `/action install` para reinstalar a versão completa.
```
