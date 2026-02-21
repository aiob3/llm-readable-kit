---
name: memora-frontend
description: >
  Expert frontend designer for the Memora MCP memory system with Postgres/SQLite backend.
  Use this skill whenever the user wants to build, improve, or refactor any UI component
  connected to Memora — including knowledge graph visualization, memory CRUD forms,
  entity/observation tables, search panels, or any dashboard that calls /api/graph,
  /api/memories, or /api/views. Also trigger when the user mentions "grafo de memória",
  "interface do Memora", "visualizar nodes/relations", "painel de conhecimento", or
  asks to design frontend for MCP Memory, SQLite memoria.db, or the canonical Postgres
  schema (canonical_context, canonical_event_log). Always apply the Memora Design System
  defined in this skill. Never skip the API contract section before generating components.
---

# Memora Frontend Skill

Você é especialista em design e engenharia frontend para o sistema **Memora MCP** —
uma interface de memória persistente baseada em grafo de conhecimento, com backend
SQLite local (memoria.db) e integração opcional com Postgres canônico.

---

## 🏗️ Arquitetura de dados

### APIs locais (fonte primária)
| Endpoint | Método | Retorno |
|---|---|---|
| `/api/graph` | GET | `{ nodes: [...], edges: [...] }` |
| `/api/memories` | GET/POST | Lista ou criação de memórias |
| `/api/views` | GET | Views pré-computadas do grafo |

### Schema SQLite (memoria.db)
```sql
memories         -- id, content, type, created_at, updated_at
memories_crossrefs  -- memory_id, ref_id, rel_type
memories_actions    -- memory_id, action, payload, ts
```

### Schema Postgres canônico (pilot/canonical-ssot-v1)
```sql
canonical_context       -- contexto de sessão/projeto
canonical_identity      -- entidades identificadas
canonical_role_catalog  -- catálogo de papéis
canonical_zone_catalog  -- zonas de memória
canonical_acl_binding   -- controle de acesso
canonical_event_log     -- log imutável de eventos (append-only)
```

> Quando o usuário não especificar a fonte, assuma SQLite via APIs locais.
> Para integração direta Postgres, usar `pg` (Pool + DATABASE_URL).

---

## 🎨 Memora Design System (MDS)

### Paleta de cores (dark mode — sempre ativo)
```css
:root {
  /* Background hierarchy */
  --mds-bg-base:    #0D0F14;
  --mds-bg-surface: #141720;
  --mds-bg-elevated:#1C2030;
  --mds-bg-overlay: #242840;

  /* Accent — graph nodes */
  --mds-accent-primary:  #6C8EFF;  /* entity nodes */
  --mds-accent-memory:   #A78BFA;  /* memory nodes */
  --mds-accent-relation: #34D399;  /* edges/relations */
  --mds-accent-action:   #FBBF24;  /* actions/events */
  --mds-accent-danger:   #F87171;  /* delete/error */

  /* Text */
  --mds-text-primary:   #E8EAED;
  --mds-text-secondary: #9AA3B2;
  --mds-text-muted:     #555E72;

  /* Border */
  --mds-border:       #2A2F42;
  --mds-border-focus: #6C8EFF;

  /* Graph specific */
  --mds-node-glow:  rgba(108,142,255,0.3);
  --mds-edge-color: rgba(52,211,153,0.6);
}
```

### Tipografia
```css
--mds-font-mono: 'JetBrains Mono', 'Fira Code', monospace; /* IDs, código */
--mds-font-ui:  'Inter', system-ui, sans-serif;             /* Interface */
--mds-font-size-xs: 11px;
--mds-font-size-sm: 13px;
--mds-font-size-md: 15px;
--mds-font-size-lg: 18px;
```

### Componentes base
```css
/* Card */
.mds-card {
  background: var(--mds-bg-surface);
  border: 1px solid var(--mds-border);
  border-radius: 10px;
  padding: 16px;
}

/* Badge de tipo */
.mds-badge {
  font-family: var(--mds-font-mono);
  font-size: var(--mds-font-size-xs);
  padding: 2px 8px;
  border-radius: 4px;
  background: var(--mds-bg-overlay);
  color: var(--mds-accent-primary);
}

/* Input */
.mds-input {
  background: var(--mds-bg-base);
  border: 1px solid var(--mds-border);
  color: var(--mds-text-primary);
  border-radius: 6px;
  padding: 8px 12px;
  font-size: var(--mds-font-size-sm);
}
.mds-input:focus { border-color: var(--mds-border-focus); outline: none; }
```

---

## 📦 Stack de componentes

### Quando usar cada stack
| Cenário | Stack |
|---|---|
| Artifact interativo completo | React + Tailwind + recharts/D3 |
| Componente isolado para embed | HTML/CSS/JS single-file |
| Grafo visual complexo | React + D3 (`d3` lib disponível) |
| Tabela com filtros/sort | React + shadcn/ui Table |
| Formulário CRUD | React + controlled inputs |

### Libs disponíveis em artifacts React
- `d3` — grafo de knowledge graph
- `recharts` — charts de métricas
- `lucide-react@0.263.1` — ícones
- `lodash` — utilities

---

## 🕸️ Componente: Grafo Visual

### Padrão obrigatório para grafo de nodes/relations
```jsx
// Cores por tipo de node (usar sempre)
const NODE_COLORS = {
  entity:   '#6C8EFF',
  memory:   '#A78BFA',
  relation: '#34D399',
  action:   '#FBBF24',
  default:  '#555E72'
};

// Estrutura de dados esperada da /api/graph
// { nodes: [{id, label, type, observations}], edges: [{source, target, type}] }

// Usar d3.forceSimulation com:
// - forceLink (distância 120)
// - forceManyBody (strength -300)
// - forceCenter
// - forceCollide (radius 30)
```

### UX obrigatória no grafo
- ✅ Zoom/pan com `d3.zoom()`
- ✅ Hover mostra tooltip com `label + type + contagem de observations`
- ✅ Click em node abre painel lateral com detalhes
- ✅ Nodes com glow effect via `filter: drop-shadow`
- ✅ Edges com seta direcional (marker-end)
- ✅ Legenda de cores dos tipos no canto inferior

---

## 📋 Componente: Tabela de Entidades/Memórias

### Estrutura obrigatória
```jsx
// Colunas padrão para /api/memories
const COLUMNS = ['ID', 'Conteúdo', 'Tipo', 'Crossrefs', 'Criado em'];

// Features obrigatórias
// - Busca por texto (filtra content)
// - Filtro por type (dropdown)
// - Sort por created_at
// - Paginação (20 por página)
// - Click em linha → expande observations inline
// - Botões de ação: Edit | Delete (com confirmação)
```

---

## 📝 Componente: Formulário CRUD

### Padrão de campos por entidade
```jsx
// memory form
{ content: textarea, type: select, tags: multi-input }

// crossref form  
{ memory_id: text, ref_id: text, rel_type: select }

// Validação obrigatória
// - Campos required com border vermelho
// - Submit button disabled durante loading
// - Feedback de sucesso/erro inline (sem alert())
// - POST para /api/memories com JSON body
```

---

## 🔌 Padrão de fetch para APIs locais

```javascript
// Sempre usar este padrão — sem axios, fetch nativo
async function fetchGraph() {
  try {
    const res = await fetch('/api/graph');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    // Mostrar erro no componente, nunca console.log apenas
    setError(err.message);
  }
}

// Para Postgres direto (pilot mode)
// Usar variável DATABASE_URL via process.env
// Pool com max: 10, idleTimeoutMillis: 30000
```

---

## ✅ Checklist antes de gerar qualquer componente

Antes de escrever código, responder internamente:
- [ ] Qual API alimenta este componente? (`/api/graph` | `/api/memories` | `/api/views` | Postgres direto)
- [ ] Qual schema de dados? (SQLite memoria.db | canonical Postgres)
- [ ] Stack correto para o contexto? (React artifact | HTML single-file)
- [ ] Design System MDS aplicado? (cores, tipografia, dark mode)
- [ ] UX obrigatória do componente incluída?
- [ ] Estado de loading e erro tratados?

---

## 🚫 Anti-patterns — nunca fazer

- `alert()` ou `confirm()` nativos — usar UI inline
- Cores hardcoded sem usar variáveis CSS `--mds-*`
- Light mode ou tema sem definição explícita
- Chamar Postgres diretamente sem Pool configurado
- Grafo sem zoom/pan
- Tabela sem paginação (para listas > 20 itens)
- `localStorage` em artifacts (não suportado)

---

## 📁 Referências complementares

- `references/api-contract.md` — exemplos de payloads reais das APIs
- `references/postgres-schema.md` — DDL completo do schema canônico
