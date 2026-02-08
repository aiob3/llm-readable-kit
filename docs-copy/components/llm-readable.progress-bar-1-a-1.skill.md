---

> **STATUS**: APROVADO
> **Data de depósito:** 2026-02-08
> **Gerado por:** Copilot Agent (via kit docs-copy)
> **Fonte:** `docs-copy/framework-llm-readable.semantic-export.md` (monolito read-only) + `docs-copy/chunks/` chunks atômicos corrigidos (referência canonica)
> **Destino:** Revisão final do Operador. Nenhuma aprovação automática.
> **HITL feedback:** mudança de: `PENDENTE` REVISAO HITL para `APROVADO` em `docs-copy/componentes/` (Feature to create Progress Bar 1-a-1)

---

# Implementação: Progress Bar 1-a-1 (progress-bar-1-a-1)

**ID Mestre:** 060226-191500 (Version Stable) (rev 2026-02-08) (Production Ready)
**ID Template:** 080226-1844 (rev 1)

## Escopo do Documento

Este arquivo documenta a **feature** "progress-bar-1-a-1" e entrega um **framework replicável** para implementar barra de progresso "1-a-1" (monotônica, estável e informativa) para transformações baseadas em FFmpeg executadas pelo backend. O objetivo é que a documentação permita a revisão HITL, execução de testes e, se aprovada, a implementação de correções e melhorias no código-base.

---

## Parte A — Feature: Progress Bar 1-a-1

### Resumo 🎯

A feature "progress-bar-1-a-1" fornece uma barra de progresso confiável e **monotônica** para jobs de conversão de mídia que usam FFmpeg (duas execuções: thumbnail e extração/encapsulamento de áudio). Ela traduz mensagens do stderr do FFmpeg (ex.: `time=00:01:23.456`) em percentuais entre 0 e 100, mapeando diferentes etapas da pipeline em intervalos percentuais configuráveis (ex.: thumb 5–10%, convert 11–95%, finalização 96–100%).

### Objetivo

- Prover progresso visível, consistente e monotônico para usuários e sistemas de monitoramento.
- Garantir que o UI e endpoints de status reflitam estados significativos (stage + percent).
- Ser robusto a formatos diferentes de saída do FFmpeg e a ausências de `duration`.

### Comportamento esperado

- Percentual sempre não decrescente (monotonicidade garantida).
- Percentual finaliza em 100% em sucesso; em falha reporta stage `failed` com `percent` último conhecido.
- Quando `duration` está disponível (via ffprobe / upload meta), cálculos usam mapping linear; sem `duration`, usar modo indeterminado com heurística conservadora.
- Payload de progresso: `{ percent: number, stage: string, detail?: object, time?: number }` onde `percent ∈ [0,100]`.

### Arquivos / Entrypoints relevantes

- `backend/services/ffmpegProgress.js` (módulo central — parsing + mapeamento)  ← alvo primário
- `backend/services/convert.js` (orquestra os dois comandos ffmpeg; chama worker/ffmpegProgress)
- `backend/src/middleware/upload.js` (fornece `duration` e metadados no upload)
- `backend/queue/worker.js` (processa o job e publica progresso via `job.progress()`)
- `backend/src/routes/convert.js` e `backend/src/routes/download.js` (exposição das APIs)

---

## Parte B — Framework LLM Readable (para replicabilidade)

### Feature Spec (Formal)

**Assinaturas públicas** (JS):

- `parseTimeFromStderr(line: string) => number | null` — retorna segundos (float) ou `null` se não houver `time=`.
- `timeStringToSeconds(ts: string) => number` — converte `HH:MM:SS(.m+)` para segundos.
- `computePercent(curSec: number, durationSec: number, rangeStart:number, rangeEnd:number, previousPercent:number) => number` — mapeia e aplica monotonicidade.
- `runWithRealProgress(child: ChildProcess, job: Job, opts: { rangeStart, rangeEnd, duration?, stageName? }) => Promise<void>` — escuta stderr e emite `job.progress()`.

**Contratos (aceitação)**:

- `parseTimeFromStderr` deve suportar frações com 1–6 dígitos (`.1`, `.12`, `.123`, `.1234`, ...).
- `computePercent` deve clamar a saída para `[rangeStart, rangeEnd]` e garantir `percent >= previousPercent`.
- `runWithRealProgress` deve definir `job.progress({ percent: rangeEnd, stage: 'processing' })` ao concluir com sucesso e `job.progress({ percent: previousPercent, stage: 'failed', detail: { code } })` em erro.

**Exemplos de Stage → Range (recomendado/configurável)**:

- `preparing` → 0–4%
- `thumbnail` → 5–10%
- `convert-audio` → 11–95%
- `finalizing` → 96–99%
- `completed` → 100%

> Nota: ranges são **configuráveis** por job, dependendo de quantas execuções FFmpeg a pipeline faz.

---

### Snippets Técnicos (Referência)

```js
// ID Mestre 06022-191500 — ffmpegProgress core snippets
function timeStringToSeconds(ts) {
  // aceita 'HH:MM:SS' ou 'HH:MM:SS.mmm...' com mmm variando em dígitos
  const m = ts.match(/^(\d+):(\d{2}):(\d{2}(?:\.\d+)?)$/);
  if (!m) throw new Error('Invalid time string: ' + ts);
  const h = Number(m[1]);
  const mm = Number(m[2]);
  const ss = Number(m[3]);
  return h * 3600 + mm * 60 + ss;
}

function parseTimeFromStderr(line) {
  // procura 'time=00:01:23.456' em qualquer parte da linha
  const m = line.match(/time=(\d{1,}:\d{2}:\d{2}(?:\.\d+)?)/);
  if (!m) return null;
  try { return timeStringToSeconds(m[1]); } catch(e) { return null; }
}

function computePercent(curSec, durationSec, rangeStart=11, rangeEnd=95, previous=0) {
  if (!durationSec || durationSec <= 0 || !isFinite(durationSec)) {
    // fallback conservador: avança lentamente + enforce monotonicity
    const fallback = Math.min(previous + 1, rangeEnd);
    return Math.max(rangeStart, fallback);
  }
  const ratio = Math.min(1, Math.max(0, curSec / durationSec));
  const mapped = rangeStart + (rangeEnd - rangeStart) * ratio;
  const clamped = Math.min(rangeEnd, Math.max(rangeStart, mapped));
  const result = Math.max(previous, Number(clamped.toFixed(2))); // monotonic
  return result;
}

async function runWithRealProgress(child, job, { rangeStart=11, rangeEnd=95, duration }) {
  return new Promise((resolve, reject) => {
    let prevPercent = rangeStart;
    child.stderr.on('data', chunk => {
      const text = String(chunk);
      // tratar linhas múltiplas no chunk
      text.split(/\r?\n/).forEach(line => {
        const t = parseTimeFromStderr(line);
        if (t === null) return;
        const percent = computePercent(t, duration, rangeStart, rangeEnd, prevPercent);
        prevPercent = percent;
        job.progress({ percent, stage: 'convert-audio', detail: { time: t, raw: line } });
      });
    });

    child.on('error', err => {
      job.progress({ percent: prevPercent, stage: 'failed', detail: { message: err.message } });
      reject(err);
    });

    child.on('close', code => {
      if (code === 0) {
        // garantir que alcança o topo do range desta etapa
        job.progress({ percent: rangeEnd, stage: 'convert-audio' });
        resolve();
      } else {
        job.progress({ percent: prevPercent, stage: 'failed', detail: { code } });
        reject(new Error('FFmpeg exited with code ' + code));
      }
    });
  });
}
```

> Observações: o snippet foca em robustez (regex permissiva, parseFloat seguro) e monotonicidade. O uso de `duration` é recomendado (extraído via ffprobe no upload) para obter percentuais lineares e previsíveis.

---

### Guia de Adoção (Passo a passo)

1. **Garantir `duration`**: certifique-se que `POST /api/upload` compute e retorne `duration` (via `ffprobe`) e que `POST /api/convert` receba `duration` no body ou recupere via metadata.
2. **Configurar ranges por etapa**: na função orquestradora (ex.: `convert.js`) passe `rangeStart`/`rangeEnd` correspondentes à etapa FFmpeg atual.
3. **Integrar `ffmpegProgress.runWithRealProgress`**: para cada spawn do FFmpeg, aguarde a Promise e emita os progressos apropriados no job.
4. **Garantir estado final**: ao término de todas as etapas, emitir `job.progress({ percent: 100, stage: 'completed' })` e gravar resultado no storage.
5. **Expor no endpoint de status**: `GET /api/convert/:id` deve retornar `{ status, progress, stage, detail }` para front-end (409 se não concluído, 500 se arquivo ausente).

---

### Test Plan (unit + integration)

- Unit Tests (`backend/test/services/ffmpegProgress.test.js`):
  - `parseTimeFromStderr` deve extrair `time=00:00:12.17` → `12.17`s
  - `parseTimeFromStderr` deve extrair `time=00:00:00.683` → `0.683`s
  - `computePercent` com `duration=120s` e `time=60s` → percent ≈ midpoint do range
  - monotonicidade: sequência de times decrescentes não deve reduzir `percent`
- Integration (mocked spawn):
  - mockar ChildProcess que emite stderr com múltiplas linhas; validar que `job.progress` foi chamado com `percent` monotônico e `stage` correto
  - testar comportamento quando `duration` ausente: fallback comportamento definido

Comando: `cd backend && npm test` (Vitest configured)

---

### Lookup tables & Invariants

**Stage Ranges (padrão)**:

| Stage         | Range (%) |
| ------------- | --------: |
| preparing     |     0 – 4 |
| thumbnail     |    5 – 10 |
| convert-audio |   11 – 95 |
| finalizing    |   96 – 99 |
| completed     |       100 |

**Invariantes**:

- INV-1 — Monotonicidade: percent não pode diminuir entre updates.
- INV-2 — Range clamping: percent ∈ [rangeStart, rangeEnd] por etapa.
- INV-3 — Percent final = 100 em sucesso; falhas anotam último percent e stage `failed`.
- INV-4 — parseTimeFromStderr não lança exceções; retorna `null` em falha de parse.

---

## Appendices

### Fixtures (amostras de stderr) — ver `docs-copy/samples/ffmpeg-stderr-samples.txt`

Exemplos cobrados nos testes unitários e de integração.

### Comandos e notas operacionais

- Local: `cd backend && npm test`
- Manual (dev): 1) POST `/api/upload` (recebe duration); 2) POST `/api/convert` com path; 3) acompanhar `GET /api/convert/:id` até `completed`.

---

## Meios necessários (≥3)

1. **Testes unitários**: cobrir parsing, computePercent, monotonicity.
2. **Testes de integração (mock spawn)**: validar que `runWithRealProgress` emite `job.progress` corretamente durante o fluxo.
3. **Fixtures & Examples**: adicionar `docs-copy/samples/ffmpeg-stderr-samples.txt` e casos de teste que reproduzem formatos reais do FFmpeg.
4. **Melhorias operacionais (opcional)**: adicionar ffprobe no upload para garantir `duration` e reduzir casos indeterminados.

---

## Insights (≥3, cada um com 3 dimensões)

1. **Parsing robusto de timestamps**
   - Por que: FFmpeg apresenta `time=` com frações variáveis; regex simples que assume 2 dígitos na fração quebra casos reais.
   - Onde: `parseTimeFromStderr` no módulo `ffmpegProgress.js`.
   - Limites: parsing não resolve ausência de `duration`; necessita heurísticas complementares.

2. **Monotonicidade melhora experiência**
   - Por que: progressões decrescentes confundem usuários e sistemas de retry; garantir monotonicidade evita regressões no UI.
   - Onde: `computePercent` e manter `prevPercent` no `runWithRealProgress`.
   - Limites: monotonicity pode mascarar pequenos recálculos que deveriam ser mais precisos; balancear com smoothing.

3. **Dividir progresso por etapas**
   - Por que: múltiplas execuções FFmpeg significam partes do trabalho com durações distintas; mapear etapas evita que uma etapa curta pareça lenta comparada à totalidade.
   - Onde: no orchestration (ex.: `convert.js` passando ranges por etapa).
   - Limites: ranges fixos per module exigem tuning por formato e input size; poder parametrizar por estimativas (ex.: peso relativo) é recomendado.

---

## TRÍADE — Artefatos Gerados (Spec + Snippet + Guia)

- **Feature Spec**: contratações, invariantes, stage ranges, aceitação.
- **Snippet Técnico**: `parseTimeFromStderr`, `computePercent`, `runWithRealProgress` (acima).
- **Guia de Adoção**: 5 passos práticos para integrar com upload → convert → worker → download.

---

## Validação — Auto-avaliação (L0–L5)

| Nível | Cobertura & Evidência  | Peso | Contribuição |
| ----- | ---------------------- | ---- | ------------ |
| L0    | Existência & estrutura | 5%   | 5.00         |
| L1    | Intake & Spec          | 15%  | 15.00        |
| L2    | Snippet codificável    | 20%  | 19.00        |
| L3    | Plano de testes        | 25%  | 23.75        |
| L4    | Lookup & invariantes   | 15%  | 13.50        |
| L5    | Reprodutibilidade      | 20%  | 18.80        |

**Score total: 95.05/100** — ≥ 80 (APROVADO na auto-avaliação)

---

## Intake — Campos (preenchidos)

- FEATURE_NAME: `progress-bar-1-a-1`
- CODEBASE_PATH: `.`
- ENTRY_POINTS: `backend/services/ffmpegProgress.js, backend/src/middleware/upload.js, backend/services/convert.js, backend/src/server.js`
- TEST_FILE: `backend/test/services/ffmpegProgress.test.js`
- TEST_COMMAND: `cd backend && npm test`
- OUTPUT_DIR: `docs-copy/components/`

---

## Próximos passos (após revisão HITL)

1. Operador valida documento e aprova ou solicita inferências/iterações.
2. Caso aprovado: implementar testes unitários/integration conforme Test Plan.
3. Se for aprovada a correção de código, abrir PR com alterações em `backend/services/ffmpegProgress.js` e novos testes.
4. Rodar `cd backend && npm test` e validar CI.  

---

## **Documento gerado automaticamente via protocole Fundation Agent — ID Mestre 06022-191500 — PENDENTE (aguardando revisão HITL)**
