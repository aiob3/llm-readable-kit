# Chunk 08 — Validação, Scoring & Testes

**ID Mestre:** 06022-191500  
**Preocupação:** Como verificar que a implementação está correta  
**Dependências:** nenhuma (chunk autocontido)  
**Fonte:** `framework-llm-readable.semantic-export.md` (Validação + Scoring + Critérios de Aceite)

---

## Critérios de Aceite (feature Export for AI / LLM)

- [x] 3 formatos de output funcionais (json, natural, prompt)
- [x] Parsing resiliente a URI-encoding duplo e control characters
- [x] Campos ausentes tratados como neutros (sem crash)
- [x] Feedback loops detectados e classificados (reinforcing/balancing)
- [x] Copy to clipboard com fallback
- [x] Download como .json ou .txt
- [x] Stats exibidos (components, relationships, loops)
- [x] Testes Jest PASS

**Status:** Feature 100% implementada e homologada.

---

## Comandos de teste

```bash
# Suíte completa (obrigatório após mudanças em mywai/js/**)
npm test -- --runInBand --watchAll=false

# Apenas SemanticExport
npx jest tests/SemanticExport.test.js --runInBand

# Validação manual via dev server
npm run dev
# → Abrir mywai/index.html → criar diagrama → Sidebar → Export for AI
# → Verificar 3 formatos + Copy + Download
```

## Cobertura de testes existente (16 testes)

| Função              | Testes | Cenários cobertos                                                                                                         |
| ------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------- |
| `parseModelData`    | 10     | simple, +space, newlines, tabs, CR, multiple nodes, edge payload, missing polarity, undefined polarity, container payload |
| `toSemanticJSON`    | 3      | simple, newlines, missing polarity                                                                                        |
| `toNaturalLanguage` | 1      | basic generation                                                                                                          |
| `toLLMPrompt`       | 2      | basic, custom question                                                                                                    |
| `findLoops`         | 1      | missing polarity handling                                                                                                 |

## Cobertura ausente (oportunidades de extensão)

- Containers com members resolvidos
- Múltiplos loops simultâneos (reinforcing vs balancing)
- Grafos densos / edge cases de deduplicação
- Integração Modal → SemanticExport
- Groups na saída de `toSemanticJSON`
- FeedbackLoops seção no `toNaturalLanguage`
- Download/clipboard (requer browser real)

---

## Auto-avaliação Logarítmica

> **Nota:** scores abaixo são auto-atribuídos durante o processo de documentação pelo Fundation Agent protocol. Não foram validados externamente.

| Nível     | Aspecto               | Cobertura | Peso | Contribuição  |
| --------- | --------------------- | --------- | ---- | ------------- |
| L0        | Existência            | 100%      | 5%   | 5.00          |
| L1        | Estrutura Declarativa | 100%      | 15%  | 15.00         |
| L2        | Schema Formal         | 95%       | 20%  | 19.00         |
| L3        | Instanciação          | 95%       | 25%  | 23.75         |
| L4        | Rastreabilidade       | 90%       | 15%  | 13.50         |
| L5        | Metacognição          | 95%       | 20%  | 19.00         |
| **Total** |                       |           |      | **96.25/100** |

**Status: APROVADO** (≥ 80)

---

## Checklist Final do Fundation Agent

- [x] Intake completo (6/6 campos)?
- [x] Meios derivados (≥3 meios documentados)?
- [x] Insights extraídos (≥3 com 3 dimensões)?
- [x] Tríade produzida (Spec + Snippet + Guia)?
- [x] ID Mestre aplicado?
- [x] Tags de taxonomia atribuídas (≥3)?
- [x] Teste mínimo reproduzível definido?
- [x] Score ≥ 80/100 na auto-avaliação?

---

## Próximos passos recomendados (feature)

- Formato de projeção `mermaid` (Mermaid.js)
- Projeção `cytoscape-json` (Cytoscape.js)
- Projeção `owl/rdf` (ontologias formais)
- Campo `question` customizável na UI (formato LLM Prompt)
- Integração com `AgentConnector.js` (ws://localhost:7000)
- Compatibilidade com UI nova (`?ui=new` — `FloatingMenu.js`)
