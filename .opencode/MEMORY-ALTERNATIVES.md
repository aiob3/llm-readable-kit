# Memory MCP - Alternativas e Futuro

## Status Atual

O `memory-keeper` está **DESABILITADO** neste workspace devido a dependência nativa (`better-sqlite3`) que requer compilação no Windows.

---

## Alternativas Disponíveis

### 1. Memora (Recomendada para Futuro)

**Instalação:**
```bash
pip install memora
```

**Recursos:**
- SQLite para armazenamento local (funciona offline)
- Full-text search
- Semantic search com embeddings
- Cross-references entre memórias
- Tag hierarchies para organização
- Sync opcional com cloud (R2/S3)
- Funciona com: Claude Code, Claude Desktop, Cursor, Codex, OpenCode

**Configuração OpenCode:**
```json
{
  "mcp": {
    "memora": {
      "type": "local",
      "command": ["memora", "serve"],
      "enabled": true
    }
  }
}
```

**Uso:**
- "Remember that we use pytest for testing"
- Later: "What testing framework do we use?"

**GitHub:** https://github.com/agentic-mcp-tools/memora

---

### 2. mcp-memory-sqlite

**Instalação:**
```bash
npm install -g @daichi-kudo/mcp-memory-sqlite
```

**Recursos:**
- SQLite com WAL mode
- Suporte a acesso concorrente
- Drop-in replacement para server-memory

**Problema:** Também requer build nativo (better-sqlite3)

---

### 3. whenmoon-afk/claude-memory-mcp

**Instalação:**
```bash
npx -y github:whenmoon-afk/claude-memory-mcp
```

**Configuração:**
```json
{
  "mcp": {
    "claude-memory": {
      "type": "local",
      "command": ["npx", "-y", "github:whenmoon-afk/claude-memory-mcp"],
      "environment": {
        "MEMORY_DB_PATH": "G:/projetos/docs-copy/.opencode/memory/claude-memory.db",
        "DEFAULT_TTL_DAYS": "90"
      },
      "enabled": true
    }
  }
}
```

---

### 4. MCP Memory Service (doobidoo)

**Instalação:** Já vem como opção oficial em alguns clientes

**Recursos:**
- 34+ features
- 1700+ memórias em produção
- Zero database locks

**GitHub:** https://github.com/doobidoo/mcp-memory-service

---

## Servidor Atual (Ativo)

### @modelcontextprotocol/server-memory

Já está ativo neste workspace:

```json
"memory": {
  "type": "local",
  "command": ["npx", "-y", "@modelcontextprotocol/server-memory"],
  "environment": {
    "MEMORY_FILE_PATH": "G:/projetos/docs-copy/.opencode/memory/cursor-memory.json"
  },
  "enabled": true
}
```

**Limitações:**
- Armazenamento em JSONL (não SQLite)
- Busca linear (sem full-text)
- Sem suporte a acesso concorrente
- Funciona para uso solo

**Para quando precisar de mais:**
- Instalar Memora (Python) - recomendado
- Tentar compilar memory-keeper em máquina com buildtools

---

## Quando Considerar Upgrade

| Cenário | Ação |
|---------|------|
| +3 sessões simultâneas | Instalar Memora |
| Busca full-text necessária | Instalar Memora |
| +1000 memórias | Memora ou mcp-memory-sqlite |
| Uso solo, <100 memórias | Manter server-memory atual |

---

## Comandos Úteis

```bash
# Testar instalação do Memora
memora --help

# Iniciar servidor Memora
memora serve

# Adicionar ao OpenCode (futuro)
# Editar opencode.json com config do Memora
```
