# CODEX_TASK — Entry Point para Agentes Autônomos

**ID Mestre:** 06022-191500
**Data:** 2026-02-08
**Tipo:** Template genérico reutilizável
**Projeto de origem:** `.`

---

## Objetivo

Aplicar o **Fundation Agent protocol** para gerar um framework LLM-readable de uma feature de codebase. O agente deve produzir documentação estruturada que converte conhecimento tácito (código) em conhecimento explícito (framework replicável).

**Entrega obrigatória:** O resultado é depositado na pasta `docs-copy/components/` para revisão final do Operador (HITL). O Operador é o **único** que determina se a execução foi bem-sucedida ou se necessita de inferência / iteração / refatoração. Nenhum entregável é considerado aprovado até validação explícita do Operador.

---

## Variáveis de Input (operador preenche antes de acionar)

```text
FEATURE_NAME    = <preenchido pelo operador>,
CODEBASE_PATH   = <preenchido pelo operador>,
ENTRY_POINTS    = <buscar outros correlacionados ao codebase>,
TEST_FILE       = <perguntar se deseja criar caso não haja>,
TEST_COMMAND    = <perguntar se deseja criar caso não haja>,
OUTPUT_DIR      = docs-copy/components/                         # default (não alterar)
```

**Exemplo preenchido (SemanticExport — primeiro entregável):**

```text
FEATURE_NAME    = semantic-export
CODEBASE_PATH   = mywai/js/
ENTRY_POINTS    = mywai/js/SemanticExport.js, mywai/js/Modal.js, mywai/js/Sidebar.js
TEST_FILE       = tests/SemanticExport.test.js
TEST_COMMAND    = npx jest tests/SemanticExport.test.js --runInBand
OUTPUT_DIR      = docs-copy/components/
```

> **Nota:** O SemanticExport é o primeiro caso de uso que originou este kit. O entregável gerado em `docs-copy/components/` serve como **referência canônica** para futuras extrações.

---

## Workflow Sequencial

1. **Ler protocolo:** `fundation-agent.prompt.md`
2. **Ler template estrutural:** `feature-recurso-progressbar.md` (referência de convenção, outro projeto)
3. **Inspecionar codebase:** ler `ENTRY_POINTS` e `TEST_FILE`
4. **Executar pipeline do Fundation Agent:**
   - Intake (6 campos) → Derivação (meios necessários) → Insights (≥3) → Tríade (Spec + Snippet + Guia)
   - Estruturar orçamento de documentação para a versão autocontida da feature (escolha uma)?
     - Recomendado — 12.000~15.000 caracteres (completo) — 3000~5000+ tokens
     - Mínimo — 4.000~8.000 caracteres ("resumido REQUER ENFASE DEDICADA NO CONTEXTO") para cenários de pedido de extração para prompt, ex:
       - Prompts de avaliação, features menores e corelacionados abaixo:
         - Com escopo bem definido, alta estabilidade, sem lógicas algorítmicas complexas;
         - Básico em desenvolvimento (ex: prompts, custo, markdown com exceção a prompts auto contidos, etc.)/Baixa complexidade, risco, impacto, sucetibilidade a erros, retrabalho, desenvolvimento, planos de teste, implantação, documentação, validação, revisão, manutenção futura, migração, treinamento (ex: CRUD simples, validação de formulário, etc.)
   - Incluir Spec, Snippets completos, Guia e Appendix — recomendado para replicabilidade (para o completo); o mínimo pode omitir o Appendix e/ou o Guia (mas DEVE incluir Spec e Snippets E MAIOR INVESTIMENTO EM CONTEXTO para o prompt).
5. **Gerar output:** salvar em `docs-copy/components/llm-readable.<FEATURE_NAME>.skill.md`
6. **Validar:** rodar `TEST_COMMAND` + scoring L0-L5 (≥ 80/100)
7. **Depositar para revisão HITL:** o entregável em `docs-copy/components/` fica em estado **PENDENTE** até aprovação explícita do Operador
8. **Registrar:** atualizar `docs/TODO.md` e `docs/SESSION_LOG.md`

### Gate HITL (Human-in-the-Loop)

Após o passo 7, o agente **para e aguarda**. O Operador revisa o entregável em `docs-copy/components/` e decide:

| Decisão do Operador        | Ação                                                              |
| -------------------------- | ----------------------------------------------------------------- |
| **Aprovado**               | Entregável é promovido (commit + registro em SESSION_LOG)         |
| **Inferência necessária**  | Operador indica gaps; agente retorna ao passo 4 com ajustes       |
| **Iteração necessária**    | Operador pede reexecução parcial (chunk específico); agente refaz |
| **Refatoração necessária** | Operador indica reestruturação; agente revisa desde o passo 3     |

---

## Mapa de Chunks por Tipo de Tarefa

Os chunks em `chunks/` são unidades de contexto atômicas que podem ser carregadas seletivamente. Use o mapa abaixo para decidir quais carregar:

### Entender o pipeline completo

Carregar: `00-context` + `01-files` + `02-ingest` + `03-enrich` + `04-project` + `05-deliver`

### Adicionar novo formato de projeção

Carregar: `04-project` + `06-lookup-tables` + `07-invariants`

### Validar implementação existente

Carregar: `01-files` + `07-invariants` + `08-validation`

### Replicar para outro projeto

Carregar: todos os chunks + `fundation-agent.prompt.md`

### Estender lookup tables para novo domínio

Carregar: `06-lookup-tables` + `07-invariants`

### Entender detecção de loops

Carregar: `03-enrich` (contém pseudocódigo + código JS real do DFS)

---

## Critérios "Done"

- [ ] Documento `llm-readable.<FEATURE_NAME>.skill.md` criado com Parte A (Feature) + Parte B (Framework)
- [ ] Intake preenchido (6/6 campos)
- [ ] Meios necessários mapeados (≥3)
- [ ] Insights extraídos (≥3, cada um com 3 dimensões: por que, onde, limites)
- [ ] Tríade completa (Feature Spec + Snippet Técnico + Guia de Adoção)
- [ ] Lookup tables preenchidas para o domínio da feature
- [ ] Invariantes listadas
- [ ] Score ≥ 80/100 na auto-avaliação logarítmica (L0-L5)
- [ ] Testes passando: `TEST_COMMAND` → PASS
- [ ] Entregável depositado em `docs-copy/components/` para revisão
- [ ] **Aprovação HITL recebida** (Operador validou o entregável)
- [ ] Registrado em `docs-copy/TODO.md` e `docs-copy/SESSION_LOG.md`

---

## Primeiro Entregável (referência canônica)

O **SemanticExport** é o caso de uso que originou este kit. Ao executar este CODEX_TASK pela primeira vez, o agente deve gerar o entregável em `docs-copy/components/llm-readable.semantic-export.skill.md` usando como referência read-only o exemplo completo em `framework-llm-readable.semantic-export.skill.md` (raiz DESTE kit: `docs-copy/`).

Este primeiro entregável valida que o kit é **auto-suficiente**: o mesmo projeto que gerou as instruções é capaz de produzir um output independente a partir delas. O entregável em `docs-copy/components/` é a versão oficial para revisão HITL — o arquivo na raiz é documentação de processo.

---

## Inventário do Kit

| Arquivo                                           | Papel                                          | Leitura     |
| ------------------------------------------------- | ---------------------------------------------- | ----------- |
| `CODEX_TASK.md`                                   | Entry point (este arquivo)                     | Obrigatória |
| `fundation-agent.prompt.md`                       | Protocolo do agente (loop metacognitivo)       | Obrigatória |
| `feature-recurso-progressbar.md`                  | Template estrutural (outro projeto)            | Referência  |
| `framework-llm-readable.semantic-export.skill.md` | Exemplo completo homologado                    | Referência  |
| `reference_study_sop.md`                          | Contexto histórico conversacional              | Opcional    |
| `chunks/00-context.md`                            | Escopo, objetivo, pipeline 4 camadas           | Seletiva    |
| `chunks/01-files.md`                              | Arquivos-alvo e entry points                   | Seletiva    |
| `chunks/02-ingest.md`                             | Camada 0→1: parsing resiliente                 | Seletiva    |
| `chunks/03-enrich.md`                             | Camada 1→2: semântica + loops DFS              | Seletiva    |
| `chunks/04-project.md`                            | Camada 2→3: projeções multi-formato            | Seletiva    |
| `chunks/05-deliver.md`                            | Camada 3: entrega (clipboard/download)         | Seletiva    |
| `chunks/06-lookup-tables.md`                      | Tabelas de significado (SSOT)                  | Seletiva    |
| `chunks/07-invariants.md`                         | Contratos obrigatórios + regras                | Seletiva    |
| `chunks/08-validation.md`                         | Scoring, testes, checklist                     | Seletiva    |
| `docs-copy/components/`                           | Repositório de Entregáveis revisados pelo HITL | Output      |
