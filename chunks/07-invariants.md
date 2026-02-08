# Chunk 07 — Invariantes & Regras de Replicação

**ID Mestre:** 06022-191500  
**Preocupação:** Contratos obrigatórios que nunca devem ser violados  
**Dependências:** nenhuma (chunk autocontido)  
**Fonte:** `framework-llm-readable.semantic-export.md` (Invariantes + Regras de Replicação)

---

## Invariantes do Framework (contratos obrigatórios)

| ID    | Invariante                 | Descrição                                                                                                                                                                                                     |
| ----- | -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| INV-1 | Resiliência de entrada     | `parseModelData` NUNCA lança exceção; retorna `{error:msg}`                                                                                                                                                   |
| INV-2 | Campos ausentes = neutros  | `polarity undefined → 0`, `strength undefined → null`, `shape → "circle"`                                                                                                                                     |
| INV-3 | Decode de labels           | `decodeLabel` aplica até **2 iterações** de `decodeURIComponent` (duplo decode). **Nota:** `fullyDecodeURI` aplica até 5 iterações, mas atua no `parseModelData` (string inteira), não em labels individuais. |
| INV-4 | Deduplicação de loops      | Assinatura = edges ordenadas com polaridade; loops idênticos → 1                                                                                                                                              |
| INV-5 | Projeções são read-only    | Nenhuma projeção altera SemanticGraph ou Model; output é string nova                                                                                                                                          |
| INV-6 | Format-agnostic enrichment | `toSemanticJSON` é SSOT semântico; projeções consomem o mesmo graph                                                                                                                                           |

---

## Regras de Replicação

Estas regras guiam a aplicação do framework em novos projetos/features.

### REGRA 1 — Separar geometria de semântica

Projetar: labels, polaridades, tipos, loops. Geometria é input; semântica é output. Nunca expor coordenadas x/y no SemanticGraph.

### REGRA 2 — Lookup tables como camada de significado

Toda conversão "forma→papel" numa tabela explícita (ver `chunk 06-lookup-tables`). Facilita: tradução i18n, customização por domínio, auditoria.

### REGRA 3 — Detecção de propriedades emergentes

Loops NÃO existem no dado serializado. São COMPUTADOS pela topologia (DFS + polaridade). Framework deve ter camada de "inferência estrutural".

### REGRA 4 — Projeções são plugins

Cada formato = 1 função independente. Todas consomem o mesmo SemanticGraph. Adicionar formato = 0 refatoração no core.

### REGRA 5 — Resiliência > Rigidez

Input pode vir encodado, quebrado, parcial. Preferir defaults neutros a erros fatais. Cada fallback deve ser silencioso e documentado.

### REGRA 6 — Delivery são canais, não lógica

Clipboard, download, display são mecanismos de entrega. A transformação semântica termina antes de chegar aqui. Canais são substituíveis sem afetar o pipeline.

---

## Observações operacionais

- O módulo `SemanticExport.js` é vanilla JS (IIFE) sem dependências externas.
- Para testes Jest, o módulo é carregado via `vm.createContext` para isolamento.
- Servir via HTTP é recomendado (não `file://`) para compatibilidade com CSP.
- `parseModelData` aceita dados de URL (`?data=...`), strings JSON brutas, ou arrays — resiliência total.
- Campos ausentes ou indefinidos nunca geram erro — são tratados como neutros.
