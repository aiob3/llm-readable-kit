# Chunk 06 — Lookup Tables (Tabelas de Significado Semântico)

**ID Mestre:** 06022-191500  
**Preocupação:** Cópia canônica ÚNICA de todas as tabelas de conversão  
**Dependências:** nenhuma (chunk autocontido)  
**Fonte:** `framework-llm-readable.semantic-export.md` (Lookup Tables — consolidadas)

---

## Responsabilidade

Estas tabelas são a **camada de significado** entre geometria e semântica. Toda conversão "forma→papel" ou "valor→significado" está aqui. Facilita: tradução i18n, customização por domínio, auditoria, extensão.

**Este é o SSOT das tabelas** — não duplicar em outros chunks ou documentos.

---

## shapeToRole (geometria → papel sistêmico)

| Shape       | Role                      | Quando usar                                 |
| ----------- | ------------------------- | ------------------------------------------- |
| `circle`    | variable or state         | Stock básico, variável contínua             |
| `triangle`  | process or transformation | Ação que converte inputs em outputs         |
| `rectangle` | storage or accumulator    | Buffer, inventário, acumulador              |
| `diamond`   | decision point            | Bifurcação condicional no sistema           |
| `hexagon`   | external entity           | Ator ou sistema fora da fronteira do modelo |

**Default:** shape ausente ou desconhecido → `"circle"` → `"variable or state"`

---

## polarityToSemantic (causalidade)

| Polarity | Label    | Meaning                |
| -------- | -------- | ---------------------- |
| `+1`     | positive | more A leads to more B |
| `-1`     | negative | more A leads to less B |
| `0`      | neutral  | no direct influence    |

**Default:** polarity `null` ou `undefined` → `0` → `"neutral"`

---

## lineStyleToMeaning (tipo de conexão)

| Style    | Meaning                        |
| -------- | ------------------------------ |
| `solid`  | direct connection              |
| `dashed` | delayed or indirect connection |
| `dotted` | weak or optional connection    |

**Default:** lineStyle ausente → `"solid"` → `"direct connection"`

---

## loopClassification (comportamento emergente)

| Condição            | Tipo        | Descrição                                                 |
| ------------------- | ----------- | --------------------------------------------------------- |
| `negCount % 2 == 0` | reinforcing | Crescimento/declínio exponencial — mudanças se amplificam |
| `negCount % 2 == 1` | balancing   | Estabilização — mudanças são contrabalançadas             |

Onde `negCount` = quantidade de edges com polarity < 0 no ciclo.

---

## Extensibilidade

Para adaptar a outro domínio (ex.: BPMN), substituir as tabelas:

```markdown
BPMN:
  pool      → organization
  lane      → department
  task      → activity
  gateway   → decision point
  event     → trigger
```

Para UML:

```markdown
  class     → entity
  interface → contract
  package   → module
```

As funções `shapeToRole()`, `polarityToLabel()`, `polarityToMeaning()`, `lineStyleToMeaning()` no `SemanticExport.js` consomem estas tabelas. Para customizar, alterar o corpo dessas funções.
