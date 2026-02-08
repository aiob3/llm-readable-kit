# docs-copy — Kit Fundation Agent para Extração de Features

**ID Mestre:** 06022-191500  
**Objetivo:** Kit portável e replicável para extrair frameworks LLM-readable de features de qualquer codebase.

---

## Para Codex Agent

**Ler apenas:** `CODEX_TASK.md` — é o entry point com workflow, variáveis de input, critérios done e mapa de chunks.

O agente NÃO precisa ler todos os arquivos. O `CODEX_TASK.md` indica quais chunks carregar para cada tipo de tarefa.

**Entrega:** todo output vai para `components/`. O Operador (HITL) é o **único** que aprova, solicita iteração ou refatora o entregável.

## Para Operador Humano

### Preparação (antes de acionar o Codex)

1. Copie esta pasta para o projeto-alvo (ou use in-place).
2. Abra `CODEX_TASK.md` e preencha as **variáveis de input**:
   - `FEATURE_NAME`, `CODEBASE_PATH`, `ENTRY_POINTS`, `TEST_FILE`, `TEST_COMMAND`
3. Acione o agente com o `CODEX_TASK.md` como contexto principal.

### Fluxo de leitura (humano)

```markdown
CODEX_TASK.md                      ← o que fazer (entry point)
    │
    ├→ fundation-agent.prompt.md   ← como fazer (protocolo)
    │
    ├→ feature-recurso-progressbar.md  ← modelo de estrutura (outro projeto)
    │
    ├→ chunks/                     ← instruções atômicas (seletivas)
    │   ├── 00-context.md
    │   ├── 01-files.md
    │   ├── 02-ingest.md
    │   ├── 03-enrich.md
    │   ├── 04-project.md
    │   ├── 05-deliver.md
    │   ├── 06-lookup-tables.md
    │   ├── 07-invariants.md
    │   └── 08-validation.md
    │
    ├→ components/                  ← pasta de ENTREGA (output → revisão HITL)
    │   └── framework-llm-readable.<feature>.md  (entregáveis pendentes/aprovados)
    │
    ├→ framework-llm-readable.semantic-export.md  ← exemplo completo (read-only)
    │
    └→ reference_study_sop.md      ← contexto histórico (opcional)
```

---

## Inventário de chunks

| Chunk              | Preocupação                                             | ~Linhas |
| ------------------ | ------------------------------------------------------- | ------- |
| `00-context`       | Escopo, objetivo, pipeline 4 camadas                    | ~45     |
| `01-files`         | Arquivos-alvo, entry points, API pública                | ~55     |
| `02-ingest`        | Camada 0→1: parsing resiliente (parseModelData)         | ~100    |
| `03-enrich`        | Camada 1→2: enriquecimento semântico + findLoops DFS    | ~120    |
| `04-project`       | Camada 2→3: projeções (NL, LLM Prompt, extensibilidade) | ~90     |
| `05-deliver`       | Camada 3: entrega (modal, clipboard, download)          | ~55     |
| `06-lookup-tables` | Tabelas de significado (SSOT canônico)                  | ~55     |
| `07-invariants`    | Contratos obrigatórios + regras de replicação           | ~60     |
| `08-validation`    | Scoring L0-L5, testes, checklist, próximos passos       | ~75     |

Cada chunk é **idempotente** (carregável N vezes sem side-effect) e **atômico** (resolve 1 preocupação completa).

---

## Pasta `components/` — Entrega e Revisão HITL

Todo entregável gerado pelo agente é depositado em `components/`. O ciclo de vida é:

```markdown
[Agente gera] → components/framework-llm-readable.<feature>.md (PENDENTE)
     │
     ▼
[Operador revisa] → Aprovado? → commit + registro em SESSION_LOG
                  → Iterar?   → agente ajusta e re-deposita
                  → Refatorar? → agente revisa desde codebase
```

O Operador (HITL) é a **única autoridade** que determina se o entregável é aceito. O agente nunca auto-aprova.

### Primeiro entregável

O SemanticExport (feature Export for AI / LLM) é o caso de uso que originou este kit. O primeiro `components/framework-llm-readable.semantic-export.md` valida que o kit é **auto-suficiente** — o mesmo projeto que gerou as instruções produz um output independente a partir delas.

---

## Convenção de nomes

- Output do processo: `framework-llm-readable.<feature-kebab>.md`
- Chunks: `chunks/NN-<preocupação>.md` (numeração sequencial)

---

## Checklist acionável (por projeto)

- [ ] Variáveis preenchidas no `CODEX_TASK.md`
- [ ] Feature real escolhida e codebase inspecionada
- [ ] Intake completo (6/6 campos)
- [ ] Meios necessários mapeados (≥3)
- [ ] Insights extraídos (≥3 com 3 dimensões)
- [ ] Tríade produzida (Spec + Snippet + Guia)
- [ ] Score ≥ 80/100 na auto-avaliação
- [ ] Documento final salvo com ID Mestre
- [ ] Testes passando
- [ ] Entregável depositado em `components/`
- [ ] **Aprovação HITL recebida** (Operador validou)
- [ ] Registrado em TODO.md + SESSION_LOG.md
