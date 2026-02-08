# Chunk 01 — Arquivos-Alvo & Entry Points

**ID Mestre:** 06022-191500  
**Preocupação:** Quais arquivos ler, modificar e testar  
**Dependências:** nenhuma  
**Fonte:** `framework-llm-readable.semantic-export.md` (Arquivos alterados)

---

## Arquivos principais (runtime)

| Arquivo                                                  | Papel                                                                                  | ~Linhas |
| -------------------------------------------------------- | -------------------------------------------------------------------------------------- | ------- |
| `mywai/js/SemanticExport.js`                             | Módulo IIFE: parseModelData, toSemanticJSON, toNaturalLanguage, toLLMPrompt, findLoops | ~525    |
| `mywai/js/Modal.js` (bloco `export_ai`, ~linhas 490-630) | Página modal com seleção de formato, textarea, copy, download                          | ~140    |
| `mywai/js/Sidebar.js` (linha ~843)                       | Entry point: `mini_button` → `publish("modal", ["export_ai"])`                         | 1       |
| `mywai/js/FloatingMenu.js` (linha ~54)                   | Entry point alternativo (UI nova, `?ui=new`)                                           | 1       |

## Testes

| Arquivo                        | Cobertura                                                                                                              |
| ------------------------------ | ---------------------------------------------------------------------------------------------------------------------- |
| `tests/SemanticExport.test.js` | ~180 linhas, 16 testes: parseModelData (10), toSemanticJSON (3), toNaturalLanguage (1), toLLMPrompt (2), findLoops (1) |

## Entry points (fluxo de acionamento)

```markdown
Sidebar.js (mini_button onclick)
    └→ publish("modal", ["export_ai"])
         └→ Modal.js (página export_ai)
              └→ Model.serialize() → SemanticExport.toXxx() → display/copy/download

FloatingMenu.js (botão action)
    └→ publish("modal", ["export_ai"])  (mesmo fluxo)
```

## API pública do SemanticExport

```js
SemanticExport.parseModelData(data)         // string|Array → { nodes, edges, containers } | { error }
SemanticExport.toSemanticJSON(data)         // string|Array → SemanticGraph | { error }
SemanticExport.toNaturalLanguage(data)      // string|Array → string (markdown)
SemanticExport.toLLMPrompt(data, question?) // string|Array → string (prompt)
SemanticExport.findLoops(nodes, edges)      // Array, Array → Loop[]
```

## Comandos de teste

```bash
# Suíte completa
npm test -- --runInBand --watchAll=false

# Apenas SemanticExport
npx jest tests/SemanticExport.test.js --runInBand

# Validação manual
npm run dev  # → abrir mywai/index.html → criar diagrama → Sidebar → Export for AI
```
