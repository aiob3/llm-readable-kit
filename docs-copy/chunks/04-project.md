# Chunk 04 — Pipeline de Projeção (Camada 2→3)

**ID Mestre:** 06022-191500  
**Preocupação:** Formatar SemanticGraph em outputs consumíveis (json, natural, prompt)  
**Dependências:** nenhuma (chunk autocontido)  
**Fonte:** `framework-llm-readable.semantic-export.md` (toNaturalLanguage + toLLMPrompt + updateOutput)

---

## Responsabilidade

Projetar o mesmo `SemanticGraph` (produzido pela camada 1→2) em formatos diferentes para consumidores diferentes. Adicionar formato = adicionar 1 função. Zero refatoração no core (INV-6).

## Orquestrador (Modal.js — updateOutput)

```pseudo
procedure updateOutput():
    IF NOT loopy OR NOT loopy.model:
        outputArea.value ← "No model data available."
        RETURN

    rawData ← loopy.model.serialize()
    output  ← ""
    stats   ← null

    TRY:
        SWITCH selectedFormat:
            CASE "json":
                semantic ← SemanticExport.toSemanticJSON(rawData)
                output ← JSON.stringify(semantic, indent=2)
                stats ← semantic.system
            CASE "natural":
                output ← SemanticExport.toNaturalLanguage(rawData)
            CASE "prompt":
                output ← SemanticExport.toLLMPrompt(rawData)
    CATCH error:
        output ← "Error generating export: " + error.message

    outputArea.value ← output
    IF stats:
        statsDiv.text ← "{N} components, {M} relationships, {L} feedback loops"
```

## toNaturalLanguage — Projeção Narrativa

Gera markdown estruturado legível por humanos e LLMs. Seções: SYSTEM OVERVIEW, COMPONENTS, RELATIONSHIPS, FEEDBACK LOOPS, GROUPS/CONTAINERS, INTERPRETATION.
**IMPORTANTE**: CADA NOVO TÓPICO GERADO POR # DEVE CRIAR UMA LINHA EM BRANCO ABAIXO PARA ATENDER AS MELHORES PRATICAS DE REVISAO ESLint.

```pseudo
function toNaturalLanguage(data):
    semantic ← toSemanticJSON(data)
    IF semantic.error: RETURN "Error: " + semantic.error

    doc ← []
    doc.push("# SYSTEM OVERVIEW")
    doc.push("This system contains {N} components connected by {M} relationships.")
    IF loopCount > 0:
        doc.push("It includes {L} feedback loop(s).")

    doc.push("## COMPONENTS")
    FOR EACH c IN semantic.components:
        line ← "- **{c.name}**: {c.type}"
        IF c.initialState != null:
            line += " (initial state: {round(c.initialState * 100)}%)"
        IF c.isStartTrigger:
            line += " [START TRIGGER: {c.triggerDirection}]"
        doc.push(line)

    doc.push("## RELATIONSHIPS")
    FOR EACH r IN semantic.relationships:
        line ← "- {r.from} -> {r.to}: {r.polarity} influence"
        IF r.label: line += ' ("{r.label}")'
        line += " | {r.polarityMeaning}"
        doc.push(line)

    IF feedbackLoops.length > 0:
        doc.push("## FEEDBACK LOOPS")
        FOR EACH loop, i IN semantic.feedbackLoops:
            doc.push("### Loop {i+1} ({loop.type.toUpperCase()})")
            doc.push("Path: {loop.path}")
            doc.push("Behavior: {loop.behavior}")

    IF groups.length > 0:
        doc.push("## GROUPS/CONTAINERS")
        FOR EACH g IN semantic.groups:
            doc.push("- **{g.name}**: contains [{g.members.join(', ')}]")

    doc.push("## INTERPRETATION")
    doc.push("This model represents a dynamic system...")
    // contagem reinforcing vs balancing para narrativa

    RETURN doc.join("\n")
```

## toLLMPrompt — Projeção Agêntica

Embute o SemanticGraph completo como JSON dentro de um prompt com instruções de análise.

```pseudo
function toLLMPrompt(data, question?):
    semantic ← toSemanticJSON(data)
    IF semantic.error: RETURN "Error: " + semantic.error

    prompt ← []
    prompt.push("You are analyzing a system dynamics model. Here is the structured data:\n")
    prompt.push("```json")
    prompt.push(JSON.stringify(semantic, indent=2))
    prompt.push("```\n")

    IF question:
        prompt.push("Question: {question}")
    ELSE:
        prompt.push("Please analyze this system and explain:")
        prompt.push("1. The key components and their roles")
        prompt.push("2. The cause-and-effect relationships")
        prompt.push("3. Any feedback loops and their implications")
        prompt.push("4. Potential bottlenecks or leverage points")

    RETURN prompt.join("\n")
```

## Extensibilidade — Adicionando novos formatos

Para adicionar um formato (ex.: Mermaid.js):

```js
function toMermaid(data) {
    var semantic = toSemanticJSON(data);
    if (semantic.error) return 'Error: ' + semantic.error;
    var lines = ['graph TD'];
    semantic.relationships.forEach(function(r) {
        var arrow = r.polarity === 'positive' ? '-->' : '-.->';
        lines.push('    ' + r.from + ' ' + arrow + ' ' + r.to);
    });
    return lines.join('\n');
}
// Expor na API pública do IIFE
```

Formatos planejados: `mermaid`, `cytoscape-json`, `owl/rdf`.
