# Workspace Docs-Copy - Estado Final

## Visão Geral do Ambiente

Este documento consolida o estado atual de toda a configuração do workspace **docs-copy**, incluindo MCPs, recursos de memória, e informações de acesso.

---

## Arquitetura Tri-CLI

Este workspace utiliza a **Convergência Tri-CLI** para maximizar capacidades de IA:

| CLI | Melhor Para | Comandos |
|-----|-------------|----------|
| **OpenCode** | Exploração, edição precisa, automação | `opencode` (esta CLI) |
| **Claude Code** | Fluxos complexos, plugins | `/commit`, `/feature-dev`, `/code-review` |
| **Codex** | Execução rápida, skills curadas | `codex <skill>` |

---

## Stack de MCPs - 9 Servidores Ativos

```
┌─────────────────────────────────────────────────────────────────────┐
│                    MCP SERVERS - STATUS                             │
├──────────────────────┬──────────────────────────────────────────────┤
│ ✅ sequential-thinking │ Raciocínio estruturado                     │
│ ✅ memory             │ Memória básica JSONL                       │
│ ✅ github             │ Integração GitHub                          │
│ ✅ postgres          │ Banco SSOT (pg_ssot.vcia.com.br)           │
│ ✅ chrome-devtools   │ DevTools Chrome                            │
│ ✅ firecrawl         │ Web Scraping                               │
│ ✅ exa               │ Busca código/docs (Exa API)                │
│ ✅ browserbase       │ Automação de Browser                       │
│ ✅ memora            │ Memória persistente avançada + Graph        │
└──────────────────────┴──────────────────────────────────────────────┘
```

---

## Detalhamento dos MCPs

### 1. sequential-thinking
- **Status**: ✅ Conectado
- **Função**: Raciocínio estruturado em múltiplas etapas
- **Uso**:Pensamento sequencial para problemas complexos

### 2. memory (server-memory)
- **Status**: ✅ Conectado
- **Armazenamento**: JSONL (`cursor-memory.json`)
- **Local**: `G:/projetos/docs-copy/.opencode/memory/cursor-memory.json`
- **Função**: Memória de contexto rápido por sessão

### 3. github
- **Status**: ✅ Conectado
- **Token**: Configurado (ghp_...)
- **Função**: Integração completa com GitHub (issues, PRs, repos)

### 4. postgres
- **Status**: ✅ Conectado
- **Database**: `ssot_mcp` em `pg_ssot.vcia.com.br:5432`
- **Usuário**: `mcp_agent`
- **Função**: Banco de dados Single Source of Truth

### 5. chrome-devtools
- **Status**: ✅ Conectado
- **Função**: Inspeção e automação via DevTools Chrome

### 6. firecrawl
- **Status**: ✅ Conectado
- **API Key**: Configurada
- **Função**: Web scraping e extração de conteúdo

### 7. exa
- **Status**: ✅ Conectado
- **URL**: `https://mcp.exa.ai/mcp`
- **Função**: Busca de código e documentação via Exa API
- **Ferramentas**: `web_search_exa`, `get_code_context_exa`, `company_research_exa`

### 8. browserbase
- **Status**: ✅ Conectado
- **API Key**: Configurada
- **Função**: Automação de browser headless

### 9. memora ⭐ NOVO
- **Status**: ✅ Conectado
- **Versão**: 0.2.22
- **Instalação**: Python (git+https://github.com/agentic-mcp-tools/memora)
- **Banco**: SQLite (`memoria.db`)
- **Graph UI**: `http://localhost:8765/graph` (iniciar manualmente)
- **Nota**: O servidor MCP Memora está ativo, mas o Graph UI deve ser iniciado separadamente

---

## Stack de Memória Persistente

### Arquitetura em Camadas

```
┌────────────────────────────────────────────────────────────────┐
│                    CAMADAS DE MEMÓRIA                         │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────────────┐     ┌──────────────────┐               │
│  │   server-memory  │     │     Memora       │               │
│  │   (JSONL)       │     │   (SQLite)       │               │
│  ├──────────────────┤     ├──────────────────┤               │
│  │ • Rápido         │     │ • Persistente    │               │
│  │ • Por sessão    │     │ • Busca semântica│               │
│  │ • Contexto      │     │ • Embeddings     │               │
│  └──────────────────┘     │ • Graph          │               │
│                           │ • TODOs/Issues   │               │
│                           │ • Cross-refs     │               │
│                           └──────────────────┘               │
│                                                                │
│  ┌──────────────────────────────────────────────────┐         │
│  │           Knowledge Graph (Memora)               │         │
│  │           http://localhost:8765/graph            │         │
│  ├──────────────────────────────────────────────────┤         │
│  │ • Visualização interativa                       │         │
│  │ • Timeline de memórias                         │         │
│  │ • Chat com RAG                                 │         │
│  │ • Filtros por tags/seções                      │         │
│  └──────────────────────────────────────────────────┘         │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## Recursos do Memora

### Ferramentas Disponíveis

| Ferramenta | Descrição |
|------------|-----------|
| `memory_create` | Criar nova memória |
| `memory_search` | Busca semântica |
| `memory_update` | Atualizar memória |
| `memory_delete` | Deletar memória |
| `memory_create_todo` | Criar TODO com status/prioridade |
| `memory_create_issue` | Criar issue com severidade |
| `memory_link` | Criar relações entre memórias |
| `memory_unlink` | Remover relações |
| `memory_boost` | Aumentar importância |
| `memory_find_duplicates` | Encontrar duplicatas com IA |
| `memory_merge` | Mesclar memórias |
| `memory_insights` | Análise de padrões |
| `memory_rebuild_embeddings` | Recalcular embeddings |
| `memory_rebuild_crossrefs` | Recalcular referências |
| `memory_export_graph` | Exportar grafo como HTML |
| `memory_graph` | Obter dados do grafo |

### Knowledge Graph - Visualização

**URL**: `http://localhost:8765/graph`

#### Recursos do Graph UI:
- **Details Panel**: Conteúdo, metadados, tags, memórias relacionadas
- **Timeline Panel**: Navegação cronológica
- **History Panel**: Log de todas as operações
- **Chat Panel**: Perguntas sobre memórias com RAG
- **Time Slider**: Filtrar por data
- **Filtros**: Tags e seções

#### Cores dos Nós:
- 🟣 **Tags** - Roxo
- 🔴 **Issues** - Vermelho (aberta), Laranja (em progresso), Verde (resolvida)
- 🔵 **TODOs** - Azul (aberto), Laranja (em progresso), Verde (completo), Vermelho (bloqueado)

---

## Configuração Técnica

### Arquivo Principal
- **Path**: `G:\projetos\docs-copy\opencode.json`

### Estrutura
```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "sequential-thinking": { "type": "local", "enabled": true },
    "memory": { "type": "local", "enabled": true },
    "github": { "type": "local", "enabled": true },
    "postgres": { "type": "local", "enabled": true },
    "chrome-devtools": { "type": "local", "enabled": true },
    "firecrawl": { "type": "local", "enabled": true },
    "exa": { "type": "remote", "enabled": true },
    "browserbase": { "type": "local", "enabled": true },
    "memora": { "type": "local", "enabled": true }
  }
}
```

### Diretórios
| Diretório | Path |
|-----------|------|
| Memória JSONL | `G:\projetos\docs-copy\.opencode\memory\` |
| Database Memora | `G:\projetos\docs-copy\.opencode\memory\memoria.db` |
| Graph UI | `http://localhost:8765/graph` |

---

## ⚠️ Graph UI Vazio - Explicação

O Knowledge Graph está vazio porque as memórias são criadas **durante as sessões de trabalho** pela IA, não manualmente.

### Como as memórias são criadas:
- A cada decisão técnica importante
- A cada configuração realizada
- A cada problema resolvido
- A cada aprendizado sobre o projeto

### O que devo (IA) registrar nas memórias:
- Decisões de arquitetura
- Configurações de MCPs realizadas
- Credenciais e endpoints
- Estrutura do projeto
- Preências do operador
- Soluções para problemas encontrados
- Comandos úteis descobertos

### Para o operador usar o Graph:
1. Iniciar o servidor via script do workspace:
   - Linux/WSL: `bash .opencode/start-memora-graph.sh`
   - PowerShell: `powershell -ExecutionPolicy Bypass -File .opencode\start-memora-graph.ps1`
   - CMD: `.opencode\start-memora-graph.bat`
2. Acessar: `http://localhost:8765/graph`
3. As memórias aparecerão automaticamente conforme eu (IA) criar durante as sessões

---

## Auto-Diagnóstico - Estado Atual

### Workspace: docs-copy
- **Path**: `G:\projetos\docs-copy`
- **Config**: `opencode.json` (raiz)

### Tri-CLI Ativo:
| CLI | Status |
|-----|--------|
| OpenCode | Ativo (esta sessão) |
| Claude Code | Configurado (plugins) |
| Codex | Configurado (skills) |

### MCPs (9 servidores):
| # | Nome | Tipo | Status |
|---|------|------|--------|
| 1 | sequential-thinking | local | ✅ |
| 2 | memory | local (JSONL) | ✅ |
| 3 | github | local | ✅ |
| 4 | postgres | local | ✅ |
| 5 | chrome-devtools | local | ✅ |
| 6 | firecrawl | local | ✅ |
| 7 | exa | remote | ✅ |
| 8 | browserbase | local | ✅ |
| 9 | memora | local (SQLite) | ✅ |

### Stack de Memória:
- **Camada 1**: `memory` (server-memory) - JSONL, rápido
- **Camada 2**: `memora` - SQLite + embeddings + Graph

### Recursos Disponíveis:
- Graph UI: `http://localhost:8765/graph` (iniciar manualmente)
- PostgreSQL: `pg_ssot.vcia.com.br:5432/ssot_mcp`
- Exa API: Busca código/docs em tempo real
- Firecrawl: Web scraping
- Browserbase: Automação de browser

### Decisões Técnicas Registradas:
1. Memory-keeper removido (依赖native - better-sqlite3)
2. Memora adicionado (Python, SQLite, sem build nativo)
3. Exa MCP configurado como remote (type: "remote")
4. Firecrawl renomeado para firecrawl-mcp
5. Browserbase renomeado para @browserbasehq/mcp-server-browserbase
6. Postgres URL como argumento (não env)

---

## Próximas Ações (IA deve lembrar)

### Iniciar Graph UI (Knowledge Graph)
O servidor MCP Memora está ativo, mas o Graph UI precisa ser iniciado manualmente:

```bash
# Opção 1: PowerShell (recomendado)
powershell -ExecutionPolicy Bypass -File .opencode\start-memora-graph.ps1

# Opção 2: CMD
.opencode\start-memora-graph.bat

# Opção 3: Direto
.opencode/.venv-memora/bin/memora-server --transport sse --host 127.0.0.1 --port 8000
```

**Acessar**: `http://localhost:8765/graph`

---

## Benefícios Entregues ao Operador

### ✅ Capacidades Combinadas

| Benefício | Descrição |
|-----------|-----------|
| **Persistência Total** | Memórias sobrevivem entre sessões |
| **Busca Semântica** | Encontra conceitos similares, não apenas palavras |
| **Visualização** | Graph UI interativo para explorar conexões |
| **Multi-CLI** | 3 ferramentas de IA integradas |
| **Database Local** | PostgreSQL para dados estruturados |
| **Web Scraping** | Firecrawl para extração de conteúdo |
| **Busca Exa** | Documentação e código em tempo real |
| **Automação Browser** | Browserbase para tarefas web |

---

## Próximos Passos (Opcional)

### Habilitar Busca Semântica
Adicionar ao `opencode.json`:
```json
"environment": {
  "MEMORA_EMBEDDING_MODEL": "openai",
  "OPENAI_API_KEY": "sua-chave"
}
```

### Cloud Sync (Memora)
```json
"environment": {
  "MEMORA_STORAGE_URI": "d1://account-id/database-id",
  "CLOUDFLARE_API_TOKEN": "seu-token"
}
```

---

## Próximas Ações (IA deve lembrar)

### Para próximas sessões, devo:
1. **Criar memórias** sobre cada decisão técnica tomada
2. **Registrar** configurações e preferências do operador
3. **Documentar** soluções para problemas encontrados
4. **Atualizar** este arquivo com novos aprendizados

### Prompts de exemplo para criar memórias:
```
"Remember: postgres connection uses mcp_agent user"
"Remember: we prefer memora over memory-keeper due to native dependencies"
"Remember: exa MCP uses remote type with API key in URL"
```

---

## Referências

- **OpenCode Docs**: https://opencode.ai/docs
- **Memora GitHub**: https://github.com/agentic-mcp-tools/memora
- **Graph UI**: http://localhost:8765/graph

---

*Documento gerado em: Fevereiro 2026*
*Workspace: docs-copy*
*Versão: 1.0*
