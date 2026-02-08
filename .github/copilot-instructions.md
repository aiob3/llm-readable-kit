# Copilot Instructions — docs-copy (Fundation Agent Kit)

## Propósito do Repositório

Este é um **kit portável de extração de frameworks LLM-readable** (ID Mestre: 060226-191500). Ele transforma conhecimento tácito de features de codebase em documentação estruturada e replicável, usando o protocolo **Fundation Agent** com loop metacognitivo recursivo.

**Não é um projeto de aplicação** — é um kit de documentação/extração que gera artefatos em `docs-copy/components/`.

## Estrutura e Navegação

O kit operável está em `docs-copy/` — essa é a pasta copiada para projetos-alvo:

```
docs-copy/
├── CODEX_TASK.md              ← Entry point para agentes (ler PRIMEIRO)
├── fundation-agent.prompt.md  ← Protocolo de execução (loop metacognitivo)
├── feature-recurso-progressbar.md ← Referência ESTRUTURAL (outro projeto, não copiar código)
├── framework-llm-readable.semantic-export.md ← Exemplo completo homologado (READ-ONLY)
├── chunks/00..08-*.md         ← Instruções atômicas, carregar SELETIVAMENTE por tarefa
├── components/                ← Pasta de ENTREGA — output revisado pelo Operador (HITL)
├── prompts/                   ← Prompts auxiliares
├── samples/                   ← Amostras de dados (ex: ffmpeg-stderr-samples.txt)
└── reference_study_sop.md     ← Contexto histórico conversacional (opcional)
```

### Regra de carregamento de chunks

Não carregar todos os chunks sempre. Usar o mapa em `docs-copy/CODEX_TASK.md` seção "Mapa de Chunks por Tipo de Tarefa":

- **Pipeline completo**: `00-context` + `01-files` + `02-ingest` + `03-enrich` + `04-project` + `05-deliver`
- **Novo formato de projeção**: `04-project` + `06-lookup-tables` + `07-invariants`
- **Validar implementação**: `01-files` + `07-invariants` + `08-validation`
- **Replicar para outro projeto**: todos + `fundation-agent.prompt.md`

## Workflow Obrigatório

1. Operador copia `docs-copy/` para o projeto-alvo e preenche variáveis em `docs-copy/CODEX_TASK.md` (`FEATURE_NAME`, `CODEBASE_PATH`, `ENTRY_POINTS`, etc.)
2. Agente lê `docs-copy/CODEX_TASK.md` como entry point
3. Agente executa pipeline: Intake (6 campos) → Derivação (meios) → Insights (≥3) → Tríade (Spec + Snippet + Guia)
4. Output salvo em `docs-copy/components/llm-readable.<FEATURE_NAME>.skill.md`
5. **Gate HITL**: agente PARA e aguarda aprovação do Operador — nunca auto-aprovar
6. Scoring L0-L5 ≥ 80/100 obrigatório antes de depositar

## Convenções Críticas

### Nomenclatura de arquivos

- Entregáveis: `llm-readable.<feature-kebab>.skill.md` (dentro de `docs-copy/components/`)
- Chunks: `docs-copy/chunks/NN-<preocupação>.md` (numeração sequencial, 00-08)

### Idioma

- Toda documentação e terminologia em **PT-BR**
- Código de referência e pseudocódigo podem usar inglês

### ID Mestre

- Aplicar `DDMMYY-HHMMSS` em todo documento gerado ou bloco significativo. O ID Mestre do kit é `060226-191500`.
- Formato: `DDMMYY-HHMMSS` (Dia, Mês, Ano, Hora, Minuto, Segundo) em timestamp de 24h, sem separadores GMT-3. Exemplo: `060226-191500` para 6 de fevereiro de 2026 às 19:15:00.

### Tríade obrigatória por entregável

Todo `skill.md` deve conter:

1. **Feature Spec** — problema → solução → fluxo → critérios de aceite
2. **Snippet Técnico** — assinatura + parâmetros + pseudocódigo + código real + grafo de dependências
3. **Guia de Adoção** — pré-requisitos + passos + testes + troubleshooting

### Taxonomia de tags

- Mínimo 3 tags por artefato, formato `CATEGORIA:subtopic`
- Categorias: `PROG` (progresso), `PARS` (parsing), `QUEUE` (filas), `UIFB` (UI feedback), `RESIL` (resiliência), `PIPE` (pipeline)

## Invariantes (nunca violar)

| ID    | Contrato                                                                             |
| ----- | ------------------------------------------------------------------------------------ |
| INV-1 | Funções de parsing NUNCA lançam exceção; retornam `{error:msg}`                      |
| INV-2 | Campos ausentes = neutros (ex: `polarity undefined → 0`, `shape → "circle"`)         |
| INV-3 | Labels: `decodeLabel` = 2 iterações; `fullyDecodeURI` = 5 iterações (string inteira) |
| INV-4 | Loops deduplicados por assinatura de edges ordenadas                                 |
| INV-5 | Projeções são read-only — nunca alteram SemanticGraph ou Model                       |
| INV-6 | `toSemanticJSON` é SSOT semântico; projeções consomem o mesmo graph                  |

## Scoring (Auto-avaliação Logarítmica L0-L5)

Cada entregável deve atingir ≥ 80/100. Fórmula: `Score = Σ(cobertura × peso)`:

| Nível | Aspecto                                    | Peso |
| ----- | ------------------------------------------ | ---- |
| L0    | Existência (binário)                       | 5%   |
| L1    | Estrutura declarativa                      | 15%  |
| L2    | Schema formal (templates ≥80% preenchidos) | 20%  |
| L3    | Instanciação com dados reais               | 25%  |
| L4    | Rastreabilidade (tags, refs cruzadas)      | 15%  |
| L5    | Metacognição (loop + scoring executado)    | 20%  |

Se score < 80: re-entrar no pipeline no nível deficiente. Máximo 3 iterações.

## Padrão Arquitetural: Pipeline de 4 Camadas

O framework segue o padrão `ingestão → enriquecimento → projeção → entrega`:

```
Camada 0→1: INGESTÃO       parseModelData()    string/array → ParsedModel
Camada 1→2: ENRIQUECIMENTO  toSemanticJSON()    ParsedModel → SemanticGraph
Camada 2→3: PROJEÇÃO        toNL/toLLMPrompt()  SemanticGraph → string formatada
Camada 3:   ENTREGA         Modal/clipboard     display / clipboard / download
```

Projeções são **plugins**: adicionar formato = adicionar 1 função, zero refatoração no core.

## Exemplo de Referência

O arquivo `docs-copy/components/llm-readable.semantic-export.skill.md` é o primeiro entregável aprovado e serve como **referência canônica** de formato e profundidade esperados. Ele **DEVE** ser consultado para qualquer dúvida sobre o padrão de saída.
