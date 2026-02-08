# Stack de Memória Persistente - Docs-Copy

## Visão Geral

Este workspace utiliza uma estratégia de memória em camadas para garantir persistência, busca eficiente e resiliência.

---

## Camadas de Memória Ativas

### 1. Memory (server-memory) - Ativo ✅
- **Tipo**: JSONL file storage
- ** Uso**: Memória de contexto rápido
- **Local**: `G:/projetos/docs-copy/.opencode/memory/cursor-memory.json`
- **Ferramentas**: `memory_`, `memory_read`, `memory_search`

### 2. Memora - Ativo ✅
- **Tipo**: SQLite com vector embeddings
- ** Uso**: Memória persistente avançada com busca semântica
- **Local**: `G:/projetos/docs-copy/.opencode/memory/memoria.db`
- **Ferramentas**: 
  - `memory_create` - Criar memória
  - `memory_search` - Busca semântica
  - `memory_update` - Atualizar
  - `memory_delete` - Deletar
  - `memory_create_todo` - Criar TODO
  - `memory_create_issue` - Criar issue
  - `memory_link` - Criar relações entre memórias
  - `memory_insights` - Análise de padrões
  - `memory_graph` - Visualização do grafo

### 3. Knowledge Graph (Memora) - Ativo ✅
- **URL**: `http://localhost:8765/graph`
- **Recursos**:
  - Visualização interativa do grafo de memórias
  - Painel de timeline
  - Chat com memórias (RAG)
  - Filtros por tags/seções

---

## Stack Completo de MCPs

| MCP | Status | Função |
|-----|--------|--------|
| sequential-thinking | ✅ | Raciocínio estruturado |
| memory | ✅ | Memória básica JSONL |
| github | ✅ | Integração GitHub |
| postgres | ✅ | Banco de dados SSOT |
| chrome-devtools | ✅ | DevTools Chrome |
| firecrawl | ✅ | Web scraping |
| exa | ✅ | Busca código/docs |
| browserbase | ✅ | Automação browser |
| **memora** | ✅ | **Memória persistente avançada** |

---

## Configuração Memora

### Variáveis de Ambiente

| Variável | Valor | Descrição |
|----------|-------|-----------|
| `MEMORA_DB_PATH` | `G:/projetos/docs-copy/.opencode/memory/memoria.db` | Banco SQLite local |
| `MEMORA_ALLOW_ANY_TAG` | `1` | Permitir qualquer tag |

### Opcional: Semantic Search

Para habilitar busca semântica com embeddings:

```json
{
  "environment": {
    "MEMORA_DB_PATH": "G:/projetos/docs-copy/.opencode/memory/memoria.db",
    "MEMORA_ALLOW_ANY_TAG": "1",
    "MEMORA_EMBEDDING_MODEL": "openai",
    "OPENAI_API_KEY": "sua-chave-aqui"
  }
}
```

### Opcional: Cloud Sync

Para sincronizar com Cloudflare D1 ou S3/R2:

```json
{
  "environment": {
    "MEMORA_STORAGE_URI": "d1://account-id/database-id",
    "CLOUDFLARE_API_TOKEN": "seu-token"
  }
}
```

---

## Como Usar

### Criar uma memória:
```
"Remember that this project uses pytest for testing"
```

### Buscar memórias:
```
"What testing framework do we use?"
```

### Criar um TODO:
```
"Create a TODO: Review PR #42, priority high"
```

### Criar uma issue:
```
"Create an issue: Fix login bug, severity major"
```

### Ver grafo de conhecimento:
- Abra `http://localhost:8765/graph` no navegador

---

## Quando Usar Cada Camada

| Cenário | Camada Recomendada |
|---------|-------------------|
| Contexto rápido da sessão | `memory` (server-memory) |
| Informação persistente com busca semântica | `memora` |
| Conexões entre conceitos | `memora` + Graph |
| Track de TODOs e issues | `memora` |
| Análise de padrões | `memora insights` |

---

## Recursos Avançados do Memora

### Memory Linking
```python
memory_link(from_id=1, to_id=2, edge_type="implements")
```

### Deduplicação com IA
```python
memory_find_duplicates(min_similarity=0.7, use_llm=True)
```

### Insights e Análise
```python
memory_insights(period="7d", include_llm_analysis=True)
```

### Export do Grafo
```python
memory_export_graph(output_path="graph.html")
```
