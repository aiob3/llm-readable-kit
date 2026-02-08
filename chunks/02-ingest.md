# Chunk 02 — Pipeline de Ingestão (Camada 0→1)

**ID Mestre:** 06022-191500  
**Preocupação:** Parsing resiliente de dados serializados  
**Dependências:** nenhuma  
**Fonte:** `framework-llm-readable.semantic-export.md` (Pseudocódigo parseModelData)

---

## Responsabilidade

Transformar o output bruto de `Model.serialize()` — que pode ser string URI-encoded, JSON, ou array nativo — em objetos tipados `{ nodes, edges, containers }`. Nunca lança exceção (INV-1).

## fullyDecodeURI (pré-processamento)

```pseudo
function fullyDecodeURI(str):
    previous ← null
    FOR i = 0 TO 4:                    // máximo 5 iterações
        IF str == previous: BREAK      // estabilizou
        previous ← str
        TRY: str ← decodeURIComponent(str)
        CATCH: BREAK                   // encoding inválido, parar
    RETURN str
```

## parseModelData (entry point da camada)

```pseudo
function parseModelData(data):
    IF typeof data == string:
        // NORMALIZAÇÃO: + → espaço (padrão URL)
        normalized ← data.replace(/\+/g, "%20")
        decoded ← fullyDecodeURI(normalized)

        // PARSE COM 4 FALLBACKS PROGRESSIVOS
        attempts ← [
            () → JSON.parse(decoded),                                    // 1. direto
            () → JSON.parse(sanitizeJSONStringLiterals(decoded)),        // 2. sanitiza control chars
            () → JSON.parse(cleanURLEncoding(decoded)),                  // 3. limpa URL residual
            () → JSON.parse(sanitizeJSONStringLiterals(                  // 4. combo
                    cleanURLEncoding(decoded)))
        ]
        FOR EACH attempt IN attempts:
            TRY: data ← attempt(); BREAK
            CATCH: continue
        IF still string: RETURN { error: "Failed to parse" }

    IF NOT isArray(data): RETURN { error: "Expected array" }

    // EXTRAÇÃO POSICIONAL (slots semânticos fixos)
    nodesRaw      ← data[0] ?? []
    edgesRaw      ← data[1] ?? []
    labelsRaw     ← data[2] ?? []
    containersRaw ← data[3] ?? []

    RETURN {
        nodes:      normalizeNodes(nodesRaw),
        edges:      normalizeEdges(edgesRaw),
        containers: normalizeContainers(containersRaw)
    }
```

## Normalização de nodes

```pseudo
normalizeNodes(nodesRaw):
    FOR EACH n IN nodesRaw:
        shapePayload ← scanOptionalPayload(n, from=7, key="S")
        YIELD {
            id:           n[0],
            x:            n[1],    y: n[2],
            initialValue: n[3],
            label:        decodeLabel(n[4]),   // até 2 iterações de decodeURIComponent
            hue:          n[5],
            radius:       n[6],
            shape:        shapePayload?.S ?? "circle",
            startTrigger: shapePayload?.T ?? null
        }
```

## Normalização de edges

```pseudo
normalizeEdges(edgesRaw):
    FOR EACH e IN edgesRaw:
        optPayload ← scanOptionalPayload(e, from=9, keys=["L","P"])
        YIELD {
            from:       e[0],      to: e[1],
            arc:        e[2],
            polarity:   e[3] ?? 0,           // null/undefined → 0 (neutro)
            strength:   e[5] ?? null,        // null = sem informação
            strokeSize: e[6],
            lineStyle:  e[7] ?? "solid",
            color:      e[8] ?? null,
            label:      optPayload?.L ?? null,
            labelPosition: optPayload?.P ?? null
        }
```

## Normalização de containers

```pseudo
normalizeContainers(containersRaw):
    FOR EACH c IN containersRaw:
        optPayload ← scanOptionalPayload(c, from=5, keys=["T","M"])
        YIELD {
            id:        c[0],
            x:         c[1], y: c[2], width: c[3], height: c[4],
            label:     optPayload?.T ?? null,
            memberIds: optPayload?.M ?? []
        }
```

## sanitizeJSONStringLiterals (auxiliar)

Remove control characters (`\x00-\x1F` exceto `\t\n\r`) dentro de strings JSON, preservando a estrutura do JSON.

## scanOptionalPayload (auxiliar)

Itera posições `from..end` de um array posicional buscando objetos com chaves esperadas (`key` ou `keys`). Retorna o primeiro objeto encontrado ou `null`.
