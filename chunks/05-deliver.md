# Chunk 05 — Pipeline de Entrega (Camada 3)

**ID Mestre:** 06022-191500  
**Preocupação:** Mecanismos de entrega do output ao usuário  
**Dependências:** nenhuma (chunk autocontido)  
**Fonte:** `framework-llm-readable.semantic-export.md` (Delivery procedures)

---

## Responsabilidade

Entregar a string formatada (produzida pelas projeções da camada 2→3) ao usuário via três canais: display (textarea), clipboard (copy), e download (Blob). A entrega é um **canal**, não lógica — a transformação semântica termina antes de chegar aqui.

## Modal entry point

```pseudo
procedure onUserClickExportAI():
    publish("modal", ["export_ai"])

procedure onModalShow("export_ai"):
    // Cria página modal 750×580
    highlightFormat(selectedFormat)      // default: "json"
    updateOutput()
    // Exibe: 3 botões de formato + textarea readonly + Copy + Download + statsDiv
```

## Copy to clipboard

```pseudo
procedure onCopy():
    outputArea.select()
    TRY:
        IF navigator.clipboard.writeText:
            await navigator.clipboard.writeText(outputArea.value)
        ELSE:
            document.execCommand("copy")     // fallback para HTTP ou browsers antigos
        feedback("Copied!", duration=1500ms)
    CATCH:
        feedback("Copy failed", duration=1500ms)
```

**Nota:** `navigator.clipboard` requer HTTPS ou localhost. Em HTTP puro, o fallback `execCommand("copy")` é ativado automaticamente.

## Download como arquivo

```pseudo
procedure onDownload():
    ext      ← IF selectedFormat == "json": ".json" ELSE ".txt"
    mimeType ← IF selectedFormat == "json": "application/json" ELSE "text/plain"
    blob ← new Blob([outputArea.value], type=mimeType + ";charset=utf-8")
    url  ← URL.createObjectURL(blob)
    triggerDownload(url, filename="mywai-export" + ext)
    setTimeout(() → URL.revokeObjectURL(url), 10000)  // cleanup após 10s
```

## Stats display

```pseudo
IF stats:
    statsDiv.textContent ← "{stats.componentCount} components, " +
                            "{stats.relationshipCount} relationships, " +
                            "{stats.loopCount} feedback loops"
```

Exibido abaixo da textarea na página modal. Disponível apenas no formato `json` (onde `semantic.system` é acessível diretamente).

## Dependências de browser

| API                             | Obrigatória | Fallback                       |
| ------------------------------- | ----------- | ------------------------------ |
| `navigator.clipboard.writeText` | não         | `document.execCommand("copy")` |
| `Blob`                          | sim         | — (requerido para download)    |
| `URL.createObjectURL`           | sim         | — (requerido para download)    |
| `setTimeout`                    | sim         | — (cleanup do object URL)      |
