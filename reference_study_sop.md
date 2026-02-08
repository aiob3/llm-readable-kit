> **Documento de contexto histórico.** Transcrição de conversa original que originou este kit.
> Leitura opcional — o conteúdo relevante já foi destilado em `framework-llm-readable.semantic-export.md` e nos `chunks/`.

---
User: /explain the feature created for Export to LLM AI

GitHub Copilot: Poderia уточar o que você quer exatamente sobre “Export to LLM AI”?  
- **Explicar** a feature existente?  
- **Implementar/ajustar** algo específico?  

Se puder, indique o **arquivo/trecho ativo** ou o **erro esperado/observado**.

User: Explicar a feature existente em sidebar?

GitHub Copilot: Optimizing tool selection...

Read [](file:///workspaces/mywai-1/.github/instructions/AGENT.instructions.md)

Read [](file:///workspaces/mywai-1/.github/instructions/copilot-instructions.md)

Read [](file:///workspaces/mywai-1/docs/challenges-goals.md)

Read [](file:///workspaces/mywai-1/docs/TODO.md)

Read [](file:///workspaces/mywai-1/docs/SESSION_LOG.md)

Created 2 todos

Entendi — vou alinhar o contexto antes de explicar a feature da sidebar.

## ✅ Calibração concluída

- **challenges-goals.md:** missão focada em “ponte semântica” entre conhecimento humano e IA, com ênfase em SSOT e impacto real.
- **TODO.md:** milestone **REFACTOR_TOPLEFT_MENU** está validado e aguardando aprovação do operador; UI nova (`?ui=new`) está **on hold**.
- **SESSION_LOG.md:** última entrada (2026-02-14) registra **Export for AI/LLM** como entrega homologada no ROADMAP, com notas de portas Replit e status do refactor de UI.
- **Ambiente:** não verificado nesta sessão (git status/testes não executados).

Antes de prosseguir: **a prioridade continua esta** e devo explicar a feature **na sidebar legacy** (UI atual), certo?  
Se preferir a explicação da UI nova (`?ui=new`) ou de outro painel específico, me avise.

## Próximos passos (pendentes)

- [ ] **Localizar feature Export LLM na sidebar** — _não iniciado (aguardando confirmação)_  
- [ ] **Explicar fluxo e uso da feature** — _não iniciado (aguardando confirmação)_

Se confirmar, sigo direto com a explicação detalhada.

User: Explicar a feature "export for AI / LLM" existente em sidebar 

GitHub Copilot: Searched for regex `export_ai|export for AI|LLM|semantic export|SemanticExport|llm` (`**/mywai/js/**`), 20 results

Read [](file:///workspaces/mywai-1/mywai/js/Sidebar.js#820-820), lines 820 to 940

Read [](file:///workspaces/mywai-1/mywai/js/Modal.js#360-360), lines 360 to 580

Searched for regex `LLMConverter|Semantic|export_ai|export AI|AI / LLM|llm|semantic` (`**/mywai/js/**`), 20 results

Read [](file:///workspaces/mywai-1/mywai/js/SemanticExport.js#1-1), lines 1 to 261

Read [](file:///workspaces/mywai-1/mywai/js/SemanticExport.js#260-260), lines 260 to 520

Read [](file:///workspaces/mywai-1/mywai/js/Modal.js#580-580), lines 580 to 800

Completed: *Localizar feature Export LLM na sidebar* (1/2)

Perfeito — aqui vai a explicação clara e direta da feature **“export for AI / LLM”** existente na sidebar (UI legacy).

## ✅ Onde a feature é disparada (Sidebar)

No painel **Edit** da sidebar, o botão “export for AI / LLM” chama:

- `publish("modal", ["export_ai"])` em Sidebar.js.

Isso abre o modal dedicado à exportação semântica.

## ✅ O que o modal faz (Modal.js)

Em Modal.js, existe uma página modal chamada `export_ai`. Ela cria:

- **Título e subtítulo** explicando a intenção da feature (transformar diagrama em dados estruturados).
- **Botões de formato**:
  - **Semantic JSON**
  - **Natural Language**
  - **LLM Prompt**
- **Textarea de saída** somente leitura.
- **Botões de ação**:
  - **Copy to Clipboard**
  - **Download** (gera `.json` ou `.txt` conforme o formato).

O modal chama `updateOutput()` no `onshow`.

## ✅ Como o conteúdo é gerado (SemanticExport.js)

O `updateOutput()` usa `loopy.model.serialize()` e passa o resultado para `SemanticExport`:

- **JSON Semântico**: `SemanticExport.toSemanticJSON(data)`
- **Texto Natural**: `SemanticExport.toNaturalLanguage(data)`
- **Prompt para LLM**: `SemanticExport.toLLMPrompt(data)`

O arquivo SemanticExport.js é o “cérebro” dessa exportação. Ele:

1. **Parseia o modelo serializado** (nodes, edges, labels, containers).
2. **Normaliza e interpreta**:
   - Polaridade positiva/negativa/neutral.
   - Tipo de linha (solid/dashed/dotted).
   - Tipo de shape (circle/triangle/rectangle…).
3. **Detecta loops de feedback** (reinforcing vs balancing).
4. **Agrupa containers**.
5. **Gera três formatos**:
   - JSON estruturado
   - Texto explicativo
   - Prompt pronto para LLM

Também mostra **estatísticas** no rodapé (componentes, relações, loops).

## ✅ Resultado prático para o usuário

Quando o usuário clica no botão da sidebar:

1. Abre modal com export.
2. Seleciona formato desejado.
3. Copia ou baixa o conteúdo.
4. Usa esse conteúdo direto em ChatGPT / agentes / pipelines.

## ✅ Também disponível no menu novo (UI refactor)

Mesmo com o refactor on hold, a ação também existe em:

- FloatingMenu.js  
  Ação: `modal:export_ai`

---

Se quiser, posso **mostrar exemplos reais do output** com base em um diagrama simples ou explicar **como cada campo do JSON mapeia os elementos do canvas**.

User: Agora que obteve este esclarecimento prévio leia #sym:# Fundation Agent — Prompt Oficial  para iterar recursivamente primeiro

GitHub Copilot: Created 1 todo

Perfeito — li o **#sym: Fundation Agent — Prompt Oficial** e estou pronto para iniciar o loop metacognitivo recursivo conforme o protocolo (com scoring e limite de 3 iterações).

Para começar a **Iteração 1 (Intake + Derivação + Insights)**, preciso só confirmar:

1) **Qual é a indicação da feature** que devo processar agora?  
2) **Qual é o documento‑base** (arquivo específico) que devo usar como referência?

Se quiser, posso usar como base a feature **“Export for AI / LLM”** e apontar o documento‑base correspondente, mas preciso do seu “ok” explícito.

## ✅ Todo atualizado

- [ ] Executar iteração Fundation Agent

User: 1. a feature “export for AI / LLM” existente na sidebar
2. #file:feature-recurso-progressbar.md 

GitHub Copilot: Completed: *Executar iteração Fundation Agent* (1/1)

## Resumo executivo

- Vou aplicar o protocolo do **Fundation Agent** à feature **“Export for AI / LLM”** da sidebar.
- O **documento‑base fornecido** é `docs copy/feature-recurso-progressbar.md` (sobre progresso FFmpeg), então uso **apenas como referência formal de estrutura**.
- As evidências técnicas reais vêm do código: Sidebar.js, Modal.js e SemanticExport.js.
- A feature exporta o diagrama em **JSON semântico**, **texto natural** e **prompt para LLM**.
- Entrego a tríade (Spec + Snippet + Guia), com tags e grafo de dependências.
- Score logarítmico executado (Iteração 1); sem re‑entrada.

## Mapa de meios necessários

| Meio | Mecanismo | Dados de Entrada | Telemetria | Fallback |
| --- | --- | --- | --- | --- |
| Serialização do modelo | `loopy.model.serialize()` | estado do canvas | stats de contagem | mensagem “No model data available” |
| Conversão semântica | `SemanticExport.toSemanticJSON()` | array serializado | contagem de componentes/loops | erro textual no output |
| Texto explicativo | `SemanticExport.toNaturalLanguage()` | JSON semântico | — | erro textual no output |
| Prompt para LLM | `SemanticExport.toLLMPrompt()` | JSON semântico | — | erro textual no output |
| Distribuição na UI | Modal `export_ai` com textarea | saída formatada | stats no rodapé | output vazio |
| Export/Clipboard | `navigator.clipboard`, `Blob`, `URL.createObjectURL` | texto do output | feedback “Copied!” | `document.execCommand('copy')` |

## Insights extraídos

- **Export semântico por JSON**
  - **Por que:** preserva estrutura (nodes, edges, loops) com semântica explícita para LLMs.
  - **Onde:** agentes, pipelines de análise e automações com prompts estruturados.
  - **Limites:** depende de parse estável de `Model.serialize`; erros de encoding podem degradar.

- **Texto natural como “ponte”**
  - **Por que:** torna o diagrama legível para humanos e validável antes de mandar para IA.
  - **Onde:** relatórios, revisão rápida e documentação de stakeholders.
  - **Limites:** perda de detalhes finos (ex.: `labelPos`, `strokeSize`).

- **Prompt formatado para LLM**
  - **Por que:** reduz fricção do usuário, entregando instruções prontas para análise.
  - **Onde:** ChatGPT/Claude/agents com instruções de análise sistêmica.
  - **Limites:** pode ficar longo em diagramas grandes (token budget).

- **Loops e containers como semântica avançada**
  - **Por que:** loops reforçadores/balanceadores são insights-chave em dinâmicas de sistemas.
  - **Onde:** análise sistêmica, causalidade e identificação de alavancas.
  - **Limites:** detecção de loops é combinatória; pode omitir loops em grafos densos.

---

## Tríade de artefatos (ID Mestre 06022-191500)

### A) Feature Spec: Export for AI / LLM (Sidebar)

**ID Mestre:** 06022-191500  
**Tags:** `PARS:semantic-export`, `UIFB:modal-export`, `PIPE:llm-prompt`  
**Documento-base:** `docs copy/feature-recurso-progressbar.md` (referência estrutural)

#### Problema
Usuário precisa transformar o diagrama visual em conteúdo **compreensível por IA** sem refazer manualmente a descrição do sistema.

#### Solução
Adicionar um modal de exportação que converte o modelo em **JSON semântico**, **texto natural** e **prompt para LLM**, com cópia/ download imediato.

#### Fluxo
1. Usuário clica em **“export for AI / LLM”** na sidebar.
2. Modal `export_ai` abre com os três formatos.
3. Output é gerado com `SemanticExport`.
4. Usuário copia ou baixa o conteúdo.

#### Critérios de Aceite
- [ ] Modal abre via `publish("modal", ["export_ai"])`.
- [ ] JSON semântico inclui componentes, relações e loops.
- [ ] Texto natural descreve componentes e relações.
- [ ] Prompt contém JSON e instruções padrão de análise.
- [ ] Botões **Copy** e **Download** funcionam.

#### Dependências

| Dependência | Tipo | Obrigatória |
| --- | --- | --- |
| SemanticExport.js | módulo interno | sim |
| Modal.js | UI | sim |
| Sidebar.js | UI | sim |
| Clipboard API | browser nativo | sim |
| Blob/URL API | browser nativo | sim |

#### Impacto por Camada
- **Frontend:** Sidebar.js, Modal.js, SemanticExport.js
- **Backend/Worker:** n/a

---

### B) Snippet Técnico: `SemanticExport.toSemanticJSON`

**ID Mestre:** 06022-191500  
**Tags:** `PARS:semantic-export`, `RESIL:parse-fallback`, `PIPE:llm-json`  
**Módulo sugerido:** SemanticExport.js

#### Assinatura

```js
SemanticExport.toSemanticJSON(data) → { system, components, relationships, feedbackLoops, groups }
```

#### Parâmetros

| Param | Tipo | Default | Descrição |
| --- | --- | --- | --- |
| data | string \| array | — | saída de `Model.serialize()` |

#### Retorno

| Campo | Tipo | Descrição |
| --- | --- | --- |
| system | object | contagens globais |
| components | array | nós com semântica |
| relationships | array | relações e polaridade |
| feedbackLoops | array | loops detectados |
| groups | array | containers/grupos |

#### Pseudocódigo

```pseudo
parse data → nodes/edges/containers
map nodes → components (shape meaning)
map edges → relationships (polarity meaning)
detect loops via DFS
map containers → groups
return semantic object
```

#### Código de Referência (extraído)

```js
function toSemanticJSON(data) {
  var parsed = parseModelData(data);
  if (!parsed || parsed.error) return { error: parsed.error };

  var relationships = parsed.edges.map(function(e) {
    return {
      from: nodeMap[e.from] ? nodeMap[e.from].label : 'Unknown',
      to: nodeMap[e.to] ? nodeMap[e.to].label : 'Unknown',
      polarity: getPolarityDescription(e.polarity),
      polarityMeaning: getPolarityMeaning(e.polarity),
      connectionType: getLineStyleMeaning(e.lineStyle),
      label: e.label || null,
      strength: e.strength
    };
  });

  return {
    system: { componentCount, relationshipCount, loopCount, groupCount },
    components, relationships, feedbackLoops, groups
  };
}
```

#### Grafo de dependências

SemanticExport.js → usa → `parseModelData()`  
SemanticExport.js → usa → `findLoops()`  
Modal.js → usa → `SemanticExport.toSemanticJSON()`  
Sidebar.js → aciona → `Modal` (`export_ai`)

---

### C) Guia de Adoção: Export for AI / LLM

**ID Mestre:** 06022-191500  
**Projeto de origem:** `aiob3/mywai`

#### Pré-requisitos
- [ ] SemanticExport.js carregado no bundle
- [ ] Modal.js com página `export_ai`
- [ ] Sidebar com botão que chama `publish("modal", ["export_ai"])`

#### Passos de integração
1. Copiar SemanticExport.js para o projeto derivado.
2. Criar modal com textarea read‑only e botões Copy/Download.
3. Conectar `updateOutput()` com `Model.serialize()`.

#### Testes de validação

```bash
# Ação manual: criar 2 nodes + 1 edge
# Abrir modal → verificar JSON, texto e prompt
# Copiar e colar em arquivo local
```

#### Checklist de compatibilidade
- [ ] Browser com Clipboard API
- [ ] Blob/URL API disponível
- [ ] `Model.serialize()` retorna array compatível

#### Troubleshooting

| Sintoma | Causa provável | Solução |
| --- | --- | --- |
| Output vazio | Model sem conteúdo | criar nodes/edges |
| “Error parsing model data” | encode inválido | checar `serialize()` |
| Copiar falha | clipboard bloqueado | usar fallback `execCommand` |

→ Ver: Feature Spec “Export for AI / LLM” (ID: 06022-191500)  
→ Ver: Snippet “SemanticExport.toSemanticJSON” (ID: 06022-191500)

---

## Score da auto-avaliação logarítmica (Iteração 1)

| Nível | Aspecto | Cobertura | Peso | Contribuição |
| --- | --- | --- | --- | --- |
| L0 | Existência | 100% | 5% | 5.0 |
| L1 | Estrutura Declarativa | 100% | 15% | 15.0 |
| L2 | Schema Formal | 90% | 20% | 18.0 |
| L3 | Instanciação | 85% | 25% | 21.25 |
| L4 | Rastreabilidade | 90% | 15% | 13.5 |
| L5 | Metacognição | 85% | 20% | 17.0 |
| **Total** |  |  |  | **89.75/100** |

**Status:** Aprovado (sem re‑entrada).

---

## Checklist final (8 itens)

- [x] Intake completo (6/6 campos)  
- [x] Meios derivados (≥3 meios documentados)  
- [x] Insights extraídos (≥3 com 3 dimensões)  
- [x] Tríade produzida (Spec + Snippet + Guia)  
- [x] ID Mestre aplicado  
- [x] Tags de taxonomia atribuídas (≥3)  
- [x] Teste mínimo reproduzível definido  
- [x] Score ≥ 80/100 na auto‑avaliação  

---

## ✅ Todo atualizado

- [x] Executar iteração Fundation Agent

Se quiser, faço a **Iteração 2** com refinamento (ex.: ampliar riscos, adicionar testes E2E ou mapear compatibilidade com `?ui=new`).

User: utilize sua ultima rsposta como base para aplicar inferência sobre " explicando a intenção da feature (transformar diagrama em dados estruturados)" para preparar a extração das informacoes necessárias para replicação de psudocódigo de framework LLM Readable metacognito sobre a feature a feature “export for AI / LLM” existente na sidebar

GitHub Copilot: Summarized conversation history

  

Created 6 todos

Read [](file:///workspaces/mywai-1/mywai/js/SemanticExport.js)

Read [](file:///workspaces/mywai-1/mywai/js/Modal.js#415-415), lines 415 to 635

Read [](file:///workspaces/mywai-1/docs/LLMReadable.instructions.md)

Read [](file:///workspaces/mywai-1/docs/CORE_LOGIC.md)

Starting: *Extrair pipeline de transformação* (5/6)

Agora vou verificar referências adicionais para completar a inferência — o LLMConverter e os testes associados:  

Searched for regex `LLMConverter|toSemanticJSON|toLLMPrompt|toNaturalLanguage` (`**/tests/**`), 9 results

Read [](file:///workspaces/mywai-1/docs/CORE_REFERENCES.md#1-1), lines 1 to 81

Read [](file:///workspaces/mywai-1/tests/SemanticExport.test.js)

Starting: *Produzir pseudocódigo framework* (6/6)

Com toda a evidência coletada, produzo agora a inferência metacognitiva e o pseudocódigo-framework replicável.

---

## Inferência Metacognitiva — Intenção da Feature "Export for AI / LLM"

### 1. Intenção Central (WHY)

A feature existe para resolver um **gap semântico fundamental**: diagramas visuais de dinâmica de sistemas (canvas com nodes, edges, loops) são **opacos para agentes LLM**. Um modelo visual serializado como `[[[1,200,300,0.5,"GDP",5,60]],[[1,2,0,1,null,3,0,"solid"]],...]` é legível por máquina mas **não carrega significado causal**. A feature funciona como **ponte semântica unidirecional**:

```
┌──────────────┐     ┌───────────────────┐     ┌──────────────────┐
│  Diagrama    │     │  SemanticExport   │     │  Agente LLM      │
│  Visual      │────▶│  (bridge layer)   │────▶│  (consumidor)    │
│  (canvas)    │     │                   │     │                  │
└──────────────┘     └───────────────────┘     └──────────────────┘
  representação         transformação             compreensão
  geométrica            semântica                 causal
```

**Metacognição**: o diagrama é um artefato de **Socialização** (SECI); o export é o ato de **Externalização** — codificar conhecimento tácito (layout visual, intuição causal) em conhecimento explícito (JSON estruturado, linguagem natural, prompt).

---

### 2. Pipeline de Transformação — Decomposição em Camadas

O framework opera em **4 camadas progressivas de abstração**:

```
CAMADA 0 — Serialização Bruta (Model.serialize)
  ↓  array compacto [nodes, edges, labels, containers, version]
  ↓  coordenadas x/y, hues, radii, arcs — sem semântica

CAMADA 1 — Parsing Estrutural (parseModelData)
  ↓  decodifica URI/JSON, normaliza polaridades (null→0)
  ↓  produz objetos tipados: {id, label, shape, initialValue...}
  ↓  resolve payloads opcionais: edge labels, container members

CAMADA 2 — Enriquecimento Semântico (toSemanticJSON)
  ↓  node → "component" com type/meaning (shape→role)
  ↓  edge → "relationship" com polarity→meaning
  ↓  DFS → "feedbackLoops" (reinforcing/balancing)
  ↓  container → "group" com membership

CAMADA 3 — Projeção para Consumidor (toNaturalLanguage / toLLMPrompt)
  ↓  markdown estruturado OU prompt com JSON embedido
  ↓  ready-to-paste para ChatGPT/Claude/agente
```

---

### 3. Pseudocódigo-Framework LLM Readable Metacognitivo

Este é o **framework replicável** — pode ser aplicado a qualquer sistema visual que precise exportar para consumo LLM:

```pseudocode
╔══════════════════════════════════════════════════════════════════╗
║  FRAMEWORK: Visual-to-LLM Semantic Bridge                      ║
║  Replicável para qualquer graph-based visual editor             ║
╚══════════════════════════════════════════════════════════════════╝

MODULE SemanticBridge:

  ┌─────────────────────────────────────────────────────────┐
  │ LAYER 0: INGESTÃO (Intake)                              │
  │ Propósito: aceitar dado bruto, resiliente a encoding    │
  │ Contrato: input=string|array → output=ParsedModel|Error │
  └─────────────────────────────────────────────────────────┘
  
  FUNCTION ingest(rawData):
    // DEFENSIVIDADE: aceitar múltiplos formatos de entrada
    IF typeof rawData == string:
      rawData ← fullyDecodeURI(rawData)        // desaninha %25XX
      rawData ← sanitizeControlChars(rawData)  // \n \r \t → escape
      rawData ← attemptParse(rawData, fallbacks=[
        directJSON,
        sanitizeThenJSON,
        urlCleanThenJSON,
        sanitizeAfterCleanJSON
      ])
    
    IF NOT isArray(rawData): RETURN Error("formato inválido")
    
    // EXTRAÇÃO POSICIONAL: cada slot do array tem semântica fixa
    nodesRaw      ← rawData[0]  // primitivos visuais
    edgesRaw      ← rawData[1]  // conexões causais
    labelsRaw     ← rawData[2]  // anotações livres
    containersRaw ← rawData[3]  // agrupamentos
    
    // NORMALIZAÇÃO: tratar campos ausentes como neutros (não como erro)
    FOR EACH node IN nodesRaw:
      node.shape ← detectOptionalPayload(node, key="S") ?? "circle"
      node.label ← decodeLabel(node[4])  // resolução URI aninhada
    
    FOR EACH edge IN edgesRaw:
      edge.polarity ← edge[3] ?? 0       // REGRA: ausência = neutro
      edge.strength ← edge[5] ?? null
      edge.label ← detectOptionalPayload(edge, key="L")
    
    FOR EACH container IN containersRaw:
      container.memberIds ← detectOptionalPayload(container, key="M") ?? []
    
    RETURN ParsedModel { nodes, edges, containers }


  ┌─────────────────────────────────────────────────────────┐
  │ LAYER 1: ENRIQUECIMENTO SEMÂNTICO (Enrichment)          │
  │ Propósito: transformar geometria em significado          │
  │ Contrato: ParsedModel → SemanticGraph                   │
  └─────────────────────────────────────────────────────────┘
  
  FUNCTION enrich(parsed):
    nodeIndex ← index(parsed.nodes, by=id)
    
    // COMPONENTES: forma visual → papel sistêmico
    components ← FOR EACH node IN parsed.nodes:
      YIELD {
        name:       node.label,
        id:         node.id,
        type:       shapeToRole(node.shape),   // circle→"variable"
                                                // rect→"accumulator"
                                                // diamond→"decision"
        initialState: node.initialValue,
        trigger:    node.startTrigger
      }
    
    // RELACIONAMENTOS: aresta → influência causal
    relationships ← FOR EACH edge IN parsed.edges:
      from ← nodeIndex[edge.from]
      to   ← nodeIndex[edge.to]
      YIELD {
        from:       from.label,
        to:         to.label,
        polarity:   polarityToSemantic(edge.polarity),
                    // +1 → "positive: more A leads to more B"
                    // -1 → "negative: more A leads to less B"
                    //  0 → "neutral: no direct influence"
        connection: lineStyleToMeaning(edge.lineStyle),
                    // solid → "direct"
                    // dashed → "delayed/indirect"
                    // dotted → "weak/optional"
        label:      edge.label,
        strength:   edge.strength
      }
    
    // LOOPS DE FEEDBACK: descoberta por DFS (emergência sistêmica)
    feedbackLoops ← detectLoops(parsed.nodes, parsed.edges):
      FOR EACH startNode:
        DFS(start=startNode, current=startNode, visited={start}):
          IF neighbor == start AND pathLength > 0:
            // CLASSIFICAÇÃO: contagem de polaridades negativas
            negCount ← count(pathEdges WHERE polarity < 0)
            loopType ← IF negCount % 2 == 0: "reinforcing"
                        ELSE: "balancing"
            EMIT Loop { path, type, description }
      
      // DEDUPLICAÇÃO: assinatura baseada em edges ordenadas
      RETURN unique(loops, by=edgeSignature)
    
    // AGRUPAMENTOS: containers → subsistemas
    groups ← FOR EACH container IN parsed.containers:
      members ← container.memberIds.map(id → nodeIndex[id].label)
      YIELD { name: container.label, members }
    
    RETURN SemanticGraph {
      system: { componentCount, relationshipCount, loopCount, groupCount },
      components,
      relationships,
      feedbackLoops,
      groups
    }


  ┌─────────────────────────────────────────────────────────┐
  │ LAYER 2: PROJEÇÃO (Projection)                          │
  │ Propósito: formatar para consumidor-alvo                │
  │ Contrato: SemanticGraph → string (format-specific)      │
  └─────────────────────────────────────────────────────────┘
  
  FUNCTION project(semanticGraph, format, options={}):
    
    SWITCH format:
    
      CASE "json":
        // PROJEÇÃO ESTRUTURADA: consumo programático
        RETURN JSON.stringify(semanticGraph, indent=2)
      
      CASE "natural":
        // PROJEÇÃO NARRATIVA: compreensão humana + LLM
        doc ← []
        doc.append("# SYSTEM OVERVIEW")
        doc.append(summarize(semanticGraph.system))
        
        doc.append("## COMPONENTS")
        FOR EACH c IN semanticGraph.components:
          doc.append("- **{c.name}**: {c.type} (state: {c.initialState})")
        
        doc.append("## RELATIONSHIPS")
        FOR EACH r IN semanticGraph.relationships:
          doc.append("- {r.from} → {r.to}: {r.polarity} | {r.meaning}")
        
        doc.append("## FEEDBACK LOOPS")
        FOR EACH loop IN semanticGraph.feedbackLoops:
          doc.append("### {loop.type}: {loop.path}")
          doc.append("Behavior: {loop.description}")
        
        doc.append("## INTERPRETATION")
        doc.append(generateInterpretation(semanticGraph))
        
        RETURN doc.join("\n")
      
      CASE "prompt":
        // PROJEÇÃO AGÊNTICA: ready-to-use para LLM
        prompt ← []
        prompt.append("You are analyzing a system dynamics model.")
        prompt.append("```json")
        prompt.append(JSON.stringify(semanticGraph, indent=2))
        prompt.append("```")
        
        IF options.question:
          prompt.append("Question: {options.question}")
        ELSE:
          prompt.append(DEFAULT_ANALYSIS_INSTRUCTIONS)
          // 1. Key components and roles
          // 2. Cause-and-effect relationships
          // 3. Feedback loops and implications
          // 4. Bottlenecks and leverage points
        
        RETURN prompt.join("\n")


  ┌─────────────────────────────────────────────────────────┐
  │ LAYER 3: ENTREGA (Delivery)                             │
  │ Propósito: disponibilizar ao usuário final               │
  │ Contrato: string → clipboard | download | display       │
  └─────────────────────────────────────────────────────────┘
  
  FUNCTION deliver(output, method):
    
    SWITCH method:
    
      CASE "display":
        // Modal page com textarea readonly
        modal.textarea.value ← output
        modal.stats ← computeStats(semanticGraph)
        // "{N} components, {M} relationships, {L} loops"
      
      CASE "clipboard":
        TRY navigator.clipboard.writeText(output)
        FALLBACK document.execCommand('copy')
        feedback("Copied!")
      
      CASE "download":
        ext ← IF format == "json": ".json" ELSE ".txt"
        blob ← new Blob(output, type=mimeType)
        triggerDownload(blob, "mywai-export" + ext)


  ┌─────────────────────────────────────────────────────────┐
  │ ORQUESTRAÇÃO (Orchestrator — Modal.js)                  │
  │ Fluxo completo de um export                             │
  └─────────────────────────────────────────────────────────┘
  
  ON user.click("Export for AI / LLM"):
    publish("modal", ["export_ai"])
    
  ON modal.show("export_ai"):
    rawData ← Model.serialize()         // CAMADA 0
    parsed  ← ingest(rawData)           // CAMADA 0→1
    graph   ← enrich(parsed)            // CAMADA 1→2
    output  ← project(graph, format)    // CAMADA 2→3
    deliver(output, "display")           // CAMADA 3
    
  ON user.click("Copy"):
    deliver(currentOutput, "clipboard")
    
  ON user.click("Download"):
    deliver(currentOutput, "download")


╔══════════════════════════════════════════════════════════════════╗
║  MAPA DE DECISÕES SEMÂNTICAS (Lookup Tables)                   ║
║  — Onde o "significado" é injetado na transformação            ║
╚══════════════════════════════════════════════════════════════════╝

  shapeToRole:
    circle   → "variable or state"        // stock básico
    triangle → "process or transformation" // transformação
    rectangle→ "storage or accumulator"    // buffer
    diamond  → "decision point"            // bifurcação
    hexagon  → "external entity"           // fronteira do sistema

  polarityToSemantic:
    +1 → { label: "positive",  meaning: "more A → more B" }
    -1 → { label: "negative",  meaning: "more A → less B" }
     0 → { label: "neutral",   meaning: "no direct influence" }

  lineStyleToMeaning:
    solid  → "direct connection"
    dashed → "delayed or indirect connection"
    dotted → "weak or optional connection"

  loopClassification:
    negativeCount % 2 == 0 → "reinforcing" (growth/decline amplifica)
    negativeCount % 2 == 1 → "balancing"   (estabilização)


╔══════════════════════════════════════════════════════════════════╗
║  INVARIANTES / CONTRATOS DO FRAMEWORK                          ║
╚══════════════════════════════════════════════════════════════════╝

  INV-1: Resiliência de entrada
    → parseModelData NUNCA lança exceção; retorna {error:msg}
    → aceita string (URI-encoded), string (JSON raw), array
    → trata + como espaço, %25XX como double-encoding

  INV-2: Campos ausentes = neutros (não erros)
    → polarity undefined/null → 0 (neutro)
    → strength undefined → null (sem informação)
    → shape payload ausente → "circle" (default)

  INV-3: Round-trip de labels
    → decodeLabel aplica até 5 iterações de decodeURIComponent
    → label recuperado == label original (pré-encoding)

  INV-4: Deduplicação de loops
    → assinatura = edges ordenadas com polaridade
    → loops com mesmos edges em ordem diferente → 1 único loop

  INV-5: Projeções são read-only
    → nenhuma função de projeção altera o SemanticGraph ou o Model
    → output é sempre string nova; sem side-effects

  INV-6: Format-agnostic enrichment
    → toSemanticJSON é SSOT da semântica
    → toNaturalLanguage e toLLMPrompt consomem o mesmo graph
    → adicionar novo formato = nova função project(graph, "novo")
```

---

### 4. Mapeamento Metacognitivo — Feature → Framework

| Elemento da Feature | Papel no Framework | Arquivo Canônico | Insight Metacognitivo |
|---|---|---|---|
| `Model.serialize()` | Produz dado bruto (Camada 0) | Model.js | SSOT geométrico — fonte de verdade posicional |
| `parseModelData()` | Ingestão resiliente + normalização | SemanticExport.js | Defensividade contra encodings variados garante portabilidade |
| `toSemanticJSON()` | Enriquecimento semântico (Camada 2) | SemanticExport.js | **Ponto onde geometria vira significado** — tabelas de lookup são o "dicionário" |
| `findLoops()` | Detecção emergente via DFS | SemanticExport.js | Loops não são desenhados pelo usuário — são **inferidos** pela topologia |
| `toNaturalLanguage()` | Projeção narrativa (Camada 3) | SemanticExport.js | Tradução para consumo dual (humano + LLM) |
| `toLLMPrompt()` | Projeção agêntica (Camada 3) | SemanticExport.js | Contextualiza o JSON com instruções de análise |
| Modal `export_ai` | Orquestrador + Delivery (Camada 3) | Modal.js | Interface de entrega com format-switching e export |
| Sidebar mini_button | Entry point (trigger) | Sidebar.js | Pub/sub pattern: `publish("modal", ["export_ai"])` |

---

### 5. Regras de Replicação (para aplicar este framework a outras features)

```
REGRA 1 — Separar geometria de semântica
  Nunca projetar coordenadas (x, y, radius) para o LLM.
  Projetar: labels, polaridades, tipos, loops.
  Geometria é input; semântica é output.

REGRA 2 — Lookup tables como camada de significado
  Toda conversão "forma→papel" deve existir numa tabela explícita.
  Facilita: tradução i18n, customização por domínio, auditoria.

REGRA 3 — Detecção de propriedades emergentes
  Loops de feedback NÃO existem no dado serializado.
  São COMPUTADOS pela topologia (DFS + polaridade).
  Framework deve ter camada de "inferência estrutural".

REGRA 4 — Projeções são plugins
  Cada formato de saída é uma função independente.
  Todas consomem o mesmo SemanticGraph.
  Adicionar formato = adicionar 1 função, zero refatoração.

REGRA 5 — Resiliência > Rigidez
  Input pode vir encodado, quebrado, parcial.
  Preferir defaults neutros a erros fatais.
  Cada fallback documentado.

REGRA 6 — Delivery são canais, não lógica
  Clipboard, download, display são mecanismos de entrega.
  A transformação semântica já terminou antes de chegar aqui.
  Separação de concerns estrita.
```

---

### 6. Checklist de Extração para Replicação

| # | Informação Extraída | Status |
|---|---|---|
| 1 | Pipeline completo: serialize → parse → enrich → project → deliver | Extraído |
| 2 | Tabelas de lookup semântico (shape, polarity, lineStyle, loopType) | Extraído |
| 3 | Algoritmo de detecção de loops (DFS + deduplicação) | Extraído |
| 4 | Estratégia de resiliência de parsing (4 fallbacks) | Extraído |
| 5 | Contrato de normalização (null→0, missing→default) | Extraído |
| 6 | Pattern de delivery (modal + clipboard + download) | Extraído |
| 7 | Entry point via pub/sub (`publish("modal", ["export_ai"])`) | Extraído |
| 8 | Invariantes do framework (5 contratos) | Extraído |
| 9 | Regras de replicação (6 regras) | Extraído |
| 10 | Mapeamento arquivo↔camada (8 pontos) | Extraído | 

Completed: *Produzir pseudocódigo framework* (6/6)

**Síntese final**: O pseudocódigo acima é um **framework LLM Readable metacognitivo completo** — descreve não apenas *o que* o código faz, mas *por que* cada camada existe e *como replicar* o padrão para outras features de export semântico. A chave da inferência é que a feature **não é apenas serialização** — é uma **ponte semântica** que converte representação geométrica tácita em conhecimento causal explícito, seguindo o ciclo SECI de Socialização→Externalização.

Quer que eu persista este framework como artefato em docs ou que prossiga para uma iteração de refinamento (ex.: adicionar diagramas de fluxo de dados, testes de contrato, ou mapeamento para novas projeções)?

**important**: documente e registre em #file:docs copy o arquivo `llm-readable-feature-extraction.prompt.md` utilizando como convenção os contratos adotados por #file:feature-recurso-progressbar.md  através de #file:fundation-agent.prompt.md 
