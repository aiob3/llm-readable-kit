# Chunk 03 — Pipeline de Enriquecimento (Camada 1→2)

**ID Mestre:** 06022-191500  
**Preocupação:** Conversão de geometria em semântica causal + detecção de loops  
**Dependências:** nenhuma (chunk autocontido)  
**Fonte:** `framework-llm-readable.semantic-export.md` (toSemanticJSON + findLoops)

---

## Responsabilidade

Transformar `ParsedModel { nodes, edges, containers }` em `SemanticGraph` — uma representação que contém significado causal (papéis, influências, loops, grupos) em vez de geometria (coordenadas, arcos, raios).

## toSemanticJSON (entry point da camada)

```pseudo
function toSemanticJSON(data):
    parsed ← parseModelData(data)          // reutiliza camada 0→1
    IF parsed.error: RETURN { error }

    nodeIndex ← index(parsed.nodes, by=id)

    // COMPONENTES: geometria → papel sistêmico
    components ← FOR EACH n IN parsed.nodes:
        YIELD {
            name:             n.label,
            id:               n.id,
            type:             shapeToRole(n.shape),      // ver chunk 06-lookup-tables
            shape:            n.shape,
            initialState:     n.initialValue,
            isStartTrigger:   !!n.startTrigger,
            triggerDirection:  n.startTrigger == 1 ? "increase"
                             : n.startTrigger == -1 ? "decrease"
                             : null
        }

    // RELACIONAMENTOS: arestas → influência causal
    relationships ← FOR EACH e IN parsed.edges:
        fromNode ← nodeIndex[e.from]
        toNode   ← nodeIndex[e.to]
        YIELD {
            from:            fromNode?.label ?? "Unknown",
            fromId:          e.from,
            to:              toNode?.label ?? "Unknown",
            toId:            e.to,
            polarity:        polarityToLabel(e.polarity),       // ver chunk 06
            polarityMeaning: polarityToMeaning(e.polarity),     // ver chunk 06
            connectionType:  lineStyleToMeaning(e.lineStyle),   // ver chunk 06
            label:           e.label,
            strength:        e.strength
        }

    // LOOPS: propriedade emergente via DFS
    loops ← findLoops(parsed.nodes, parsed.edges)
    loopDescriptions ← FOR EACH loop IN loops:
        path ← loop.nodes.map(n → n.label).join(" -> ")
        YIELD {
            type:     loop.type,          // "reinforcing" | "balancing"
            path:     path + " -> " + loop.nodes[0].label,
            behavior: loop.description
        }

    // GRUPOS: containers → subsistemas
    groups ← FOR EACH c IN parsed.containers:
        members ← c.memberIds.map(id → nodeIndex[id]?.label ?? "Unknown")
        YIELD { name: c.label ?? "Unnamed Group", members }

    RETURN {
        system: { componentCount, relationshipCount, loopCount, groupCount },
        components, relationships, feedbackLoops: loopDescriptions, groups
    }
```

## findLoops — Detecção de Propriedades Emergentes (DFS)

Loops de feedback **não existem no dado serializado** — são propriedades emergentes da topologia do grafo. O DFS descobre todos os ciclos e a contagem de polaridades negativas classifica automaticamente.

```pseudo
function findLoops(nodes, edges):
    nodeMap   ← index(nodes, by=id)
    adjacency ← buildAdjacencyList(nodes, edges)
    loops     ← []

    FOR EACH startId IN adjacency.keys:
        pathSet ← { startId: true }
        dfs(startId, startId, [startId], [], pathSet):

            FOR EACH neighbor IN adjacency[currentId]:
                IF neighbor.to == startId AND path.length > 0:
                    // LOOP ENCONTRADO — classificar
                    polarities ← pathEdges.map(e → e.polarity ?? 0)
                    negCount   ← count(polarities WHERE p < 0)
                    type ← IF negCount % 2 == 0: "reinforcing" ELSE "balancing"
                    loops.push({ nodes, edges, type, description })
                    CONTINUE

                IF neighbor.to IN pathSet: CONTINUE

                pathSet[neighbor.to] ← true
                RECURSE(startId, neighbor.to, path+[neighbor.to], edgePath+[edge], pathSet)
                pathSet[neighbor.to] ← false

    // DEDUPLICAÇÃO por assinatura de edges ordenadas
    seen ← {}
    RETURN loops.filter(loop →
        signature ← loop.edges.map(e → e.from+"->"+e.to+":"+e.polarity).sort().join("|")
        IF signature NOT IN seen: seen[signature] ← true; KEEP
        ELSE: DISCARD
    )
```

## Código JS real de referência (findLoops)

```js
function findLoops(nodes, edges) {
    var loops = [], nodeMap = {}, adjacency = {};
    nodes.forEach(function(n) { nodeMap[n.id] = n; adjacency[n.id] = []; });
    edges.forEach(function(e) {
        if (adjacency[e.from]) adjacency[e.from].push({ to: e.to, edge: e });
    });

    function dfs(startId, currentId, path, edgePath, pathSet) {
        var neighbors = adjacency[currentId] || [];
        for (var i = 0; i < neighbors.length; i++) {
            var nextId = neighbors[i].to;
            if (nextId === startId && path.length > 0) {
                var polarities = edgePath.concat([neighbors[i].edge]).map(function(e) {
                    return (e.polarity !== undefined && e.polarity !== null) ? e.polarity : 0;
                });
                var negCount = polarities.filter(function(p) { return p < 0; }).length;
                loops.push({
                    nodes: path.map(function(id) { return nodeMap[id]; }),
                    edges: edgePath.concat([neighbors[i].edge]),
                    type: (negCount % 2 === 0) ? 'reinforcing' : 'balancing',
                    description: (negCount % 2 === 0)
                        ? 'Exponential growth or decline - changes amplify themselves'
                        : 'Stabilizing behavior - changes are counteracted'
                });
                continue;
            }
            if (pathSet[nextId]) continue;
            path.push(nextId); edgePath.push(neighbors[i].edge); pathSet[nextId] = true;
            dfs(startId, nextId, path, edgePath, pathSet);
            pathSet[nextId] = false; path.pop(); edgePath.pop();
        }
    }

    Object.keys(adjacency).forEach(function(nodeId) {
        var numId = parseInt(nodeId, 10);
        var pathSet = {}; pathSet[numId] = true;
        dfs(numId, numId, [numId], [], pathSet);
    });

    var uniqueLoops = [], seen = {};
    loops.forEach(function(loop) {
        var sig = loop.edges.map(function(e) {
            var pol = (e.polarity !== undefined && e.polarity !== null) ? e.polarity : 0;
            return e.from + '->' + e.to + ':' + pol;
        }).sort().join('|');
        if (!seen[sig]) { seen[sig] = true; uniqueLoops.push(loop); }
    });
    return uniqueLoops;
}
```

## Retorno: SemanticGraph

| Campo           | Tipo   | Descrição                                                                                  |
| --------------- | ------ | ------------------------------------------------------------------------------------------ |
| `system`        | object | `{ componentCount, relationshipCount, loopCount, groupCount }`                             |
| `components`    | Array  | `[{ name, id, type, shape, initialState, isStartTrigger, triggerDirection }]`              |
| `relationships` | Array  | `[{ from, fromId, to, toId, polarity, polarityMeaning, connectionType, label, strength }]` |
| `feedbackLoops` | Array  | `[{ type, path, behavior }]`                                                               |
| `groups`        | Array  | `[{ name, members }]`                                                                      |
