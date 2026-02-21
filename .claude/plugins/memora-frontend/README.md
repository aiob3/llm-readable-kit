# memora-frontend Plugin

Plugin de design frontend para o sistema **Memora MCP** — orquestra automaticamente
a skill de domínio (`memora-frontend`) com a skill de qualidade estética
(`frontend-design` oficial da Anthropic).

---

## Instalação rápida (Claude Code)

```bash
# 1. Clonar ou copiar o plugin para seu projeto
cp -r memora-frontend-plugin/ .claude/plugins/memora-frontend/

# 2. Registrar no Claude Code (se necessário)
# O Claude Code detecta plugins automaticamente em .claude/plugins/

# 3. Verificar instalação
/action status
```

## Uso

```bash
/action                   # modo interativo
/action grafo             # gera grafo de nodes/relations
/action tabela            # gera tabela de memórias com filtros
/action formulario        # gera formulário CRUD
/action dashboard         # gera painel completo
/action install           # instala/atualiza as skills sem gerar código
/action status            # verifica status das skills
```

## O que o `/action` faz

```
FASE 0 → Detecta se ambas skills estão instaladas
  ↓ se faltam → instala automaticamente via curl (frontend-design)
               ou copia do plugin (memora-frontend)
FASE 1 → Lê as duas skills
FASE 2 → Briefing da tarefa
FASE 3 → Plano combinado (direção estética + contrato de API)
FASE 4 → Gera o componente com ambas skills ativas
FASE 5 → Relatório de execução
```

## Skills gerenciadas

| Skill | Fonte | Responsabilidade |
|---|---|---|
| `frontend-design` | github.com/anthropics/skills | Qualidade estética, tipografia, "inesquecível" |
| `memora-frontend` | este plugin | Domínio Memora, APIs, schema, MDS tokens |

## Estrutura do plugin

```
memora-frontend-plugin/
├── .claude-plugin/
│   └── plugin.json              ← metadados e dependências
├── commands/
│   └── action/
│       └── action.md            ← lógica do comando /action
├── skills/
│   └── memora-frontend/
│       ├── SKILL.md             ← skill principal
│       └── references/
│           ├── api-contract.md  ← payloads das APIs
│           └── postgres-schema.md ← DDL canônico
├── agents/
│   └── installer.md             ← fallback de reinstalação
└── README.md
```

## Atualizar frontend-design manualmente

```bash
curl -fsSL \
  https://raw.githubusercontent.com/anthropics/skills/main/skills/frontend-design/SKILL.md \
  -o .claude/skills/frontend-design/SKILL.md
```
