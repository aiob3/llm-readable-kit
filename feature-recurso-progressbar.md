> ⚠ **DOCUMENTO DE OUTRO PROJETO** (video2plaud — Node.js/FFmpeg/Bull/Redis).
> Serve exclusivamente como referência ESTRUTURAL para convenção de documentação.
> Não copie exemplos de código daqui para projetos vanilla JS browser-only.

# Implementação: Progresso Real 1-a-1 (feature/recurso)

**ID Mestre:** 06022-191500

## Resumo 🎯

Este documento descreve a solução implementada para prover progresso visual 1-a-1 durante a conversão de vídeo → áudio (FFmpeg). A solução combina: (1) parsing do stderr do FFmpeg para obter `time=` real da execução, (2) mapeamento da `time` para percentuais (11–95%), (3) envio de payloads estruturados `{ percent, stage, detail }` via `job.progress()` do Bull, e (4) uma UI generativa (frontend) que consome esses payloads e mostra uma barra, timeline de logs e mensagens amigáveis.

**Objetivo Expandido:** Este arquivo foi gerado com o objetivo não apenas de documentar a evolução da funcionalidade, mas também de estabelecer uma **cadeia de instruções reutilizável em formato de snippets** que possa ser replicada para outras demandas que se alinhem à necessidade de obter feedback realista sobre a evolução do estado de processamento, independente de sua fonte de entrada ou saída. O padrão descrito é aplicável tanto ao cenário original (conversão vídeo → áudio) quanto a cenários de **ingestão em lote de [N] arquivos** (ex.: processamento paralelo de múltiplos `.md`, PDFs, imagens ou outros formatos), permitindo que o mesmo pipeline de progresso 1-a-1 seja estendido para workloads em massa com rastreamento granular por item.

## Objetivo

- Evitar barreiras na UI (barra travada em 50%).
- Entregar feedback progressivo e explicativo ao usuário (estágio + detalhe).
- Permitir "componentização máxima" para fácil reutilização e testes.

---

## Arquivos alterados (principais)

- `backend/services/convert.js` — `runWithRealProgress` que parseia `time=` do stderr e envia payloads periódicos.
- `backend/queue/worker.js` — worker envia `reportProgress` e recebe `durationSec` no job payload.
- `backend/src/routes/convert.js` — aceita `duration` no POST para enfileirar o job.
- `backend/public/index.html` — frontend com UI generativa: barra 1-a-1, timeline de logs e polling de status.

---

## Procedimento para replicar (branch `feature/recurso`)

1. Crie a branch:

```bash
git checkout -b feature/recurso
```

   a. Alterações backend (resumo):

- Implementar `runWithRealProgress(args, { durationSec, rangeStart, rangeEnd, stage, detail, reportProgress })`:
  - spawn FFmpeg com `stdio: ["ignore","pipe","pipe"]`.
  - Parsear `stderr` por `time=HH:MM:SS.xx` (regex) → `currentTimeSec`.
  - Calcular `ratio = currentTimeSec / durationSec` e `percent = rangeStart + ratio * (rangeEnd-rangeStart)`.
  - Enviar `await reportProgress({ percent, stage, detail:`${detail} — ${elapsed} / ${total}`})` apenas quando `percent` aumenta (1-a-1).
- Garantir fallback para heartbeat caso parsing não funcione.

  b. Alterações queue/worker:

- Ao enfileirar, inclua `durationSec` no payload (vindo do upload ou de `ffprobe`).
- Dentro do `process` do worker, passe `reportProgress` que faz `job.progress(payload)`.

  c. Alterações frontend:

- O upload retorna `duration` e `path`. Envie `duration` ao POST `/api/convert`.
- Poll `/api/convert/:id`: a resposta inclui `{ status, progress, stage, detail }`.
- Atualize componente `Progress` para consumir `percent, stage, detail` e exibir: grande `%`, `stageLabel`, `detail`, e entrada de timeline (nova entrada ao mudar `stage`).

  d. Testes locais:

- Rebuild: `docker compose build --no-cache && docker compose up -d`
- Upload: `curl -F "file=@/path/video.mp4" http://localhost:3001/api/upload`
- Iniciar conversão: `curl -X POST -H "Content-Type: application/json" -d '{"path":"/app/uploads/temp/xxx.mp4","title":"video.mp4","duration":1271.96}' http://localhost:3001/api/convert`
- Poll: `curl http://localhost:3001/api/convert/1`
- Download: `curl -O http://localhost:3001/api/download/1`

---

## Pseudocódigo — procedimento (`feature/recurso`) 🔧

### Worker (orquestração)

```pseudo
procedure workerProcess(job):
    payload = job.data
    reportProgress = (p) -> job.progress(p)
    reportProgress({percent:1, stage:"queued", detail:"Job recebido"})
    convertToAudio({
        inputPath: payload.inputPath,
        outputName: job.id,
        title: payload.title,
        durationSec: payload.durationSec,
        reportProgress
    })
```

### convertToAudio (procedimento principal)

```pseudo
procedure convertToAudio({ inputPath, outputName, title, durationSec, reportProgress }):
    safeReport = (p) -> try reportProgress(p) catch ignore

    safeReport({percent:2, stage:"validating", detail:"Validando entrada"})

    // thumbnail
    safeReport({percent:5, stage:"thumbnail", detail:"Capturando thumbnail aos 15s"})
    exec(ffmpeg -ss 15 -i inputPath -frames:v 1 thumb.jpg)
    safeReport({percent:10, stage:"thumbnail-done", detail:"Thumbnail pronta"})

    // conversão com progresso real 10..95
    safeReport({percent:11, stage:"convert-audio", detail:"Iniciando extração"})
    runWithRealProgress(ffmpeg -i inputPath -vn -c:a aac -b:a 128k ... output.mp4,
         {durationSec, rangeStart:11, rangeEnd:95, stage:"convert-audio", detail:"Extraindo áudio", reportProgress:safeReport})

    safeReport({percent:96, stage:"faststart", detail:"Faststart"})
    safeReport({percent:98, stage:"metadata", detail: `Gravando metadados: "${title}"`})
    safeReport({percent:100, stage:"done", detail:"Concluído"})

    return {outputPath, thumbPath}
```

### runWithRealProgress (núcleo)

```pseudo
function runWithRealProgress(args, { durationSec, rangeStart, rangeEnd, stage, detail, reportProgress }):
    lastPercent = rangeStart
    spawnProcess(args)
    on stderr or stdout chunk:
        time = parseTime(chunk) // regex time=H:M:S.xx
        if time != null and durationSec > 0:
            ratio = min(time / durationSec, 1)
            percentRaw = rangeStart + ratio * (rangeEnd - rangeStart)
            percent = floor(percentRaw)
            if percent > lastPercent:
                lastPercent = percent
                reportProgress({percent, stage, detail: `${detail} — ${format(time)}/${format(durationSec)}`})
    on exit (code == 0):
        reportProgress({percent: rangeEnd, stage, detail: detail + ' — finalizado'})
```

---

## Componentização Máxima (snippet)

- Extraia `runWithRealProgress` para `services/ffmpegProgress.js` com API:

```js
export async function runWithRealProgress(args, {durationSec, rangeStart, rangeEnd, stage, detail, onProgress}) {
  // spawn & parse
}
```

- Crie `services/convert` com `convertToAudio()` que importa `runWithRealProgress`.
- Crie `workers/convertWorker` que importa `convertToAudio` e fornece `reportProgress` via `job.progress`.
- No frontend, crie componentes:
  - `Uploader` (faz upload, recebe duration & path)
  - `ProgressBar` (recebe {percent, stage, detail})
  - `Timeline` (logs de stages)
  - `ConvertController` (liga upload -> enqueue -> poll -> progress)

---

## Formato de payload e exemplo de resposta (status)

- `job.progress` envia objeto: `{ percent: Number, stage: String, detail: String }`.

- Exemplo GET `/api/convert/1` enquanto ativo:

```json
{
  "status": "active",
  "progress": 68,
  "stage": "convert-audio",
  "detail": "🎧 Extraindo áudio — 2:13 / 21:11",
  "message": "Processando...",
  "timestamp": "2026-02-07T00:00:00.000Z"
}
```

---

## Observações operacionais e testes

- Defina `FFMPEG_BIN`/`FFPROBE_BIN` se os binários não estiverem no PATH do container.
- Caso parsing falhe, o módulo pode cair para um `heartbeat` incremental (interval baseado em heurística).
- Teste com vídeos longos (>1min) para validar step resolution.

---

## Próximos passos recomendados

- Extrair `runWithRealProgress` como módulo testável com unit tests que simulam streams.
- Adicionar testes E2E (upload -> convert -> download) com arquivos "fake" (curtos) em CI.
- Ajustar UI para mostrar micro-steps (ex.: barras internas) e animações por `stage`.

---

Se quiser, eu abro um PR da branch `feature/recurso` com este arquivo e uma descrição pronta para revisão. Deseja que eu faça isso agora? ✅
