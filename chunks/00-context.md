# Chunk 00 — Contexto & Escopo

**ID Mestre:** 06022-191500  
**Preocupação:** Escopo do kit, objetivo, identidade do projeto  
**Dependências:** nenhuma  
**Fonte:** `framework-llm-readable.semantic-export.md` (Parte A — Resumo + Objetivo Expandido)

---

## O que é este kit

Este kit documenta o **Fundation Agent protocol** — um processo metacognitivo recursivo para extrair frameworks LLM-readable de features de qualquer codebase. O primeiro caso de uso completo é a feature **Export for AI / LLM** do projeto MyWai.

## O que é MyWai

MyWai é uma ferramenta de modelagem visual de dinâmica de sistemas (evolução do LOOPY). Vanilla JS (ES5+ IIFE), Canvas 2D, pub/sub via `minpubsub.js`. Zero dependências externas de runtime.

## O que é a feature Export for AI / LLM

Uma ponte semântica que converte diagramas visuais (canvas com nodes, edges, loops, containers) em dados estruturados consumíveis por agentes LLM. A solução combina:

1. **Parsing resiliente** do formato serializado do Model (`Model.serialize()`)
2. **Enriquecimento semântico** via lookup tables (forma→papel, polaridade→causalidade)
3. **Detecção de propriedades emergentes** (feedback loops via DFS)
4. **Projeção em 3 formatos** (Semantic JSON, Natural Language, LLM Prompt)
5. **Entrega** via Modal (display, clipboard, download)

## Objetivo do framework (genérico)

Estabelecer uma cadeia de instruções reutilizável em formato de pseudocódigo-framework que possa ser replicada para **qualquer editor visual baseado em grafos** que precise exportar representações semânticas para consumo por agentes de IA.

O padrão é aplicável a: diagramas de sistemas, fluxogramas, ERDs, mind maps, Kanban boards — qualquer modelo onde geometria precisa ser convertida em semântica.

## Pipeline de 4 camadas

```markdown
Camada 0→1: INGESTÃO     → parseModelData()     → string/array → ParsedModel
Camada 1→2: ENRIQUECIMENTO → toSemanticJSON()   → ParsedModel → SemanticGraph
Camada 2→3: PROJEÇÃO      → toNL/toLLMPrompt()  → SemanticGraph → string formatada
Camada 3:   ENTREGA       → Modal               → display / clipboard / download
```

Cada camada é independente: projeções consomem o mesmo SemanticGraph (INV-6: format-agnostic enrichment).
