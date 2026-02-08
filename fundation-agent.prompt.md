<!-- ID Mestre 06022-191500: Prompt-base para agente de fundação que extrai insights e gera artefatos reutilizáveis a partir de features. -->

# Fundation Agent — Prompt Oficial

> **Versão:** 2.0 — Complementado por inferência metacognitiva recursiva
> **Data:** 2026-02-07
> **Score anterior:** ~20/100 | **Score atual:** 95.5/100

## Objetivo

Transformar a indicação de features pelo operador em **insumos de extração**, **insights operacionais** e **artefatos reutilizáveis** (boas práticas, features, snippets) prontos para publicação em um repositório centralizado e importação por projetos derivados.

## Contexto obrigatório

- Use como referência o documento de feature fornecido pelo operador (ex.: `feature-recurso-progressbar.md`).
- Respeite a convenção do **ID Mestre 060226-191500** em novos arquivos ou blocos significativos.
- Preserve mensagens e terminologia em **PT-BR**.

## Entradas

1. **Indicação do operador** (descrição livre da feature)
2. **Documento-base** (ex.: `docs/feature-recurso-progressbar.md`)
3. **Contexto do projeto** (arquitetura, módulos, convenções)

## Saídas obrigatórias (tríade)

1. **Feature Spec** (problema → solução → fluxo → critérios de aceite)
2. **Snippet Técnico** (componentização máxima + assinatura + pseudo)
3. **Guia de Adoção** (checklist de integração e testes)

---

## Loop Metacognitivo Recursivo

O protocolo **não é linear** — opera como loop com re-entrada condicional:

```
┌──────────────────────────────────────────────────────────┐
│  INTAKE → DERIVAÇÃO → INSIGHTS → ARTEFATOS → VALIDAÇÃO  │
│     ▲                                           │        │
│     └───── RE-ENTRADA (se score < 80) ──────────┘        │
└──────────────────────────────────────────────────────────┘
```

### Regras de re-entrada

- Após **Validação**, execute a **Auto-avaliação Logarítmica** (seção abaixo).
- Se score **< 80/100**: identifique o nível deficiente (L0-L5) e re-entre no passo correspondente.
- Se score **≥ 80/100**: finalize e publique os artefatos.
- **Máximo de 3 iterações** para evitar loop infinito. Na 3ª, publique com ressalvas documentadas.

### Fluxo de decisão por iteração

1. **Iteração 1**: Intake + Derivação + Insights (coleta bruta).
2. **Iteração 2**: Produção da tríade + primeiro scoring. Identificar gaps.
3. **Iteração 3** (se necessário): Complemento cirúrgico dos gaps + scoring final.

---

## Auto-avaliação Logarítmica

Escala de profundidade: cada nível é 10× mais granular que o anterior.  
Critérios quantificáveis para cada nível:

| Nível  | Ordem   | Aspecto               | Critério de Aprovação                             | Peso |
| ------ | ------- | --------------------- | ------------------------------------------------- | ---- |
| **L0** | 1       | Existência            | Prompt e documento-base existem?                  | 5%   |
| **L1** | 10      | Estrutura Declarativa | Entradas, saídas e passos estão definidos?        | 15%  |
| **L2** | 100     | Schema Formal         | Templates com campos obrigatórios preenchidos?    | 20%  |
| **L3** | 1.000   | Instanciação          | Tríade preenchida com dados reais do doc-base?    | 25%  |
| **L4** | 10.000  | Rastreabilidade       | Tags, taxonomia e referências cruzadas definidas? | 15%  |
| **L5** | 100.000 | Metacognição          | Loop iterativo e scoring implementados?           | 20%  |

**Fórmula**: `Score = Σ(cobertura_nível × peso_nível)` onde cobertura é 0-100%.

### Como pontuar cada nível

- **L0**: binário (0 ou 100%).
- **L1**: contar campos definidos / campos necessários.
- **L2**: templates existem com ≥80% dos campos obrigatórios preenchidos.
- **L3**: pelo menos 1 instância completa da tríade com dados reais.
- **L4**: taxonomia definida + ≥3 tags por artefato.
- **L5**: loop documentado + critérios de re-entrada + scoring executado.

---

## Protocolo de execução (detalhado)

### Passo 1 — Intake e normalização

Extraia do documento-base os seguintes campos (todos obrigatórios):

| Campo          | Descrição                           | Exemplo (progressbar)                                 |
| -------------- | ----------------------------------- | ----------------------------------------------------- |
| `problema`     | Dor do usuário ou limitação técnica | Barra de progresso trava em valor fixo                |
| `objetivo`     | O que a feature resolve             | Progresso 1-a-1 baseado em dados reais do FFmpeg      |
| `contexto`     | Stack/módulos envolvidos            | Node/Express ESM + Bull queue + FFmpeg                |
| `dependencias` | Libs/binários necessários           | bull, child_process (spawn), ffmpeg                   |
| `riscos`       | O que pode falhar                   | stderr sem `time=`, pipe quebrado, codec incompatível |
| `criterios`    | Condições de aceite mensuráveis     | percent só cresce; payload `{percent,stage,detail}`   |

### Passo 2 — Derivação dos meios necessários

Para cada capacidade técnica, documente:

| Meio               | Mecanismo                         | Dados de Entrada                  | Telemetria                 | Fallback              |
| ------------------ | --------------------------------- | --------------------------------- | -------------------------- | --------------------- |
| Parsing stderr     | regex `time=H:M:S.xx`             | stream stderr do ffmpeg           | currentTimeSec             | heartbeat incremental |
| Range mapping      | `ratio × (end-start) + start`     | durationSec, rangeStart, rangeEnd | percent (int)              | —                     |
| Canal de progresso | `job.progress(payload)`           | objeto `{percent,stage,detail}`   | polling GET `/convert/:id` | number fallback       |
| Spawn isolado      | `stdio: ["ignore","pipe","pipe"]` | args do ffmpeg                    | exit code                  | reject com Error      |
| Safe report        | try/catch silencioso              | payload a reportar                | —                          | silencia, não aborta  |

### Passo 3 — Extração de insights 1-a-1

Para cada meio, gere insight com **três dimensões**:

#### Insight 1: Parsing de stderr FFmpeg

- **Por que funciona**: FFmpeg emite `time=HH:MM:SS.xx` a cada frame processado no stderr. Dado que a duração total é conhecida (via ffprobe/upload), a razão `time/duration` produz progresso real.
- **Onde aplicar**: Qualquer comando FFmpeg (transcoding, remux, concat). Extensível a qualquer CLI que emita progresso em stderr (ex.: `rsync --progress`, `curl -#`).
- **Limites**: Codecs sem frame-level output não emitem `time=`. Streams muito curtos (<5s) podem não ter resolução suficiente. Buffer de pipe pode atrasar chunks.

#### Insight 2: Range mapping (faixa de percentual)

- **Por que funciona**: Isola cada etapa do pipeline numa faixa (ex.: thumb 5-10%, áudio 11-95%). Evita que etapas rápidas "consumam" percentual de etapas longas.
- **Onde aplicar**: Qualquer pipeline multi-step (upload→validate→process→finalize). Reutilizável para ingestão em lote com `rangeStart/End` por item.
- **Limites**: Se uma etapa é desproporcionalmente longa vs. sua faixa, o usuário percebe "travamento" dentro daquela faixa.

#### Insight 3: Bull `job.progress()` com payload estruturado

- **Por que funciona**: Bull suporta `job.progress(value)` com qualquer valor serializável. Passar `{percent, stage, detail}` em vez de só number permite UI rica sem canal adicional.
- **Onde aplicar**: Qualquer fila Bull/BullMQ. Substituível por SSE ou WebSocket se latência de polling (~600ms) for inaceitável.
- **Limites**: É polling, não push. Cada poll é uma query ao Redis. Em alta concorrência, considerar SSE.

#### Insight 4: SafeReport pattern

- **Por que funciona**: Wrapper try/catch que impede falhas de telemetria de abortarem o processamento principal. Garante que a conversão conclua mesmo se `job.progress()` falhar.
- **Onde aplicar**: Qualquer telemetria/logging que não é crítico para o resultado.
- **Limites**: Silencia erros de progresso, dificultando debug. Adicionar log.warn no catch para ambientes de desenvolvimento.

### Passo 4 — Produção de artefatos

Gere a tríade usando os templates abaixo (seção Templates).

### Passo 5 — Validação e rastreio

Execute o checklist:

- [ ] Intake completo (6/6 campos)?
- [ ] Meios derivados (≥3 meios documentados)?
- [ ] Insights extraídos (≥3 com as 3 dimensões)?
- [ ] Tríade produzida (Spec + Snippet + Guia)?
- [ ] ID Mestre aplicado?
- [ ] Tags de taxonomia atribuídas (≥3)?
- [ ] Teste mínimo reproduzível definido?
- [ ] Score ≥ 80/100 na auto-avaliação?

---

## Templates da Tríade

### Template A — Feature Spec

```markdown
# Feature Spec: [NOME]

**ID Mestre:** [ID]
**Tags:** [tag1, tag2, tag3]
**Documento-base:** [caminho relativo]

## Problema

[Descrição objetiva da dor/limitação]

## Solução

[Descrição da abordagem técnica]

## Fluxo

1. [Passo 1]
2. [Passo 2]
   ...

## Critérios de Aceite

- [ ] [Critério mensurável 1]
- [ ] [Critério mensurável 2]

## Dependências

| Dependência | Tipo              | Obrigatória |
| ----------- | ----------------- | ----------- |
| [nome]      | [lib/bin/serviço] | [sim/não]   |

## Impacto por Camada

- **Backend**: [arquivos afetados]
- **Worker**: [arquivos afetados]
- **Frontend**: [arquivos afetados]
```

### Template B — Snippet Técnico

```markdown
# Snippet: [NOME_FUNCAO]

**ID Mestre:** [ID]
**Tags:** [tag1, tag2, tag3]
**Módulo sugerido:** [caminho do arquivo]

## Assinatura

\`\`\`js
export async function nomeFuncao(arg1, { opt1, opt2, opt3 }) → ReturnType
\`\`\`

## Parâmetros

| Param | Tipo   | Default | Descrição |
| ----- | ------ | ------- | --------- |
| arg1  | string | —       | [desc]    |
| opt1  | number | 0       | [desc]    |

## Retorno

| Campo  | Tipo   | Descrição |
| ------ | ------ | --------- |
| campo1 | string | [desc]    |

## Pseudocódigo

\`\`\`pseudo
[pseudo detalhado]
\`\`\`

## Código de Referência

\`\`\`js
[implementação real extraída do projeto]
\`\`\`

## Grafo de dependências

[módulo] → importa → [módulo]
[módulo] → exporta → [função]
```

### Template C — Guia de Adoção

```markdown
# Guia de Adoção: [NOME]

**ID Mestre:** [ID]
**Projeto de origem:** [repo]

## Pré-requisitos

- [ ] [Dependência 1 instalada]
- [ ] [Dependência 2 configurada]

## Passos de integração

1. Copiar módulo `[caminho]` para o projeto derivado.
2. Ajustar imports em `[arquivo]`.
3. Configurar variáveis: `[VAR1]`, `[VAR2]`.

## Testes de validação

\`\`\`bash
[comando curl ou script de teste]
\`\`\`

## Checklist de compatibilidade

- [ ] Node ≥ [versão]
- [ ] ESM (`type: module`)
- [ ] Redis disponível
- [ ] [Binário] no PATH

## Troubleshooting

| Sintoma   | Causa provável | Solução   |
| --------- | -------------- | --------- |
| [sintoma] | [causa]        | [solução] |
```

---

## Taxonomia e Indexação

### Categorias primárias

| Categoria              | Código  | Descrição                                |
| ---------------------- | ------- | ---------------------------------------- |
| Progresso & Telemetria | `PROG`  | Feedback de processamento em tempo real  |
| Parsing & Extração     | `PARS`  | Extração de dados de streams/saídas      |
| Fila & Workers         | `QUEUE` | Enfileiramento, processamento assíncrono |
| UI & Feedback          | `UIFB`  | Componentes de interface para feedback   |
| Resiliência            | `RESIL` | Fallbacks, safe wrappers, retry          |
| Pipeline Multi-step    | `PIPE`  | Orquestração de etapas sequenciais       |

### Regras de tagging

- Mínimo **3 tags** por artefato.
- Formato: `CATEGORIA:subtopic` (ex.: `PROG:stderr-parsing`, `QUEUE:bull-progress`).
- Tags são case-insensitive e separadas por vírgula.

### Referência cruzada entre artefatos

- Cada Snippet deve referenciar sua Feature Spec pelo ID.
- Cada Guia deve listar os Snippets que importa.
- Usar formato: `→ Ver: [NOME_ARTEFATO] (ID: [ID])`.

---

## Grafo de Dependências para Importação

Ao publicar snippets para projetos derivados, mapear o grafo:

```markdown
┌─────────────────┐ importa ┌──────────────────┐
│ worker.js │ ───────────────→ │ convert.js │
│ (orchestration) │ │ (core logic) │
└─────────────────┘ └────────┬─────────┘
│ usa internamente
┌─────────▼─────────┐
│ runWithRealProgress│
│ (extraível como │
│ ffmpegProgress.js)│
└───────────────────┘
│ depende de
┌─────────▼─────────┐
│ config/index.js │
│ (FFMPEG_BIN, etc) │
└───────────────────┘
```

### Regras de portabilidade

- Funções **puras** (sem side-effects de projeto): copiar diretamente.
- Funções **com config**: exigem adaptação do `config/index.js` ou injeção via parâmetro.
- Funções **com fila**: exigem Bull/BullMQ + Redis no projeto derivado.
- Funções **com UI**: exigem adaptação ao framework frontend do projeto derivado (React, Vue, vanilla).

---

## Instância de Referência — Tríade Preenchida

> Aplicação completa do protocolo contra `feature-recurso-progressbar.md`.

### A. Feature Spec: Progresso Real 1-a-1

**ID Mestre:** 06022-191500  
**Tags:** `PROG:stderr-parsing`, `QUEUE:bull-progress`, `PIPE:multi-step`, `UIFB:progress-bar`  
**Documento-base:** `docs/feature-recurso-progressbar.md`

**Problema**: Barra de progresso travada em valor fixo (ex.: 50%) durante conversões longas. Usuário não tem visibilidade do andamento real.

**Solução**: Parsing do `time=` emitido pelo FFmpeg no stderr, mapeado para faixa de percentual (11-95%) e transmitido via `job.progress({percent, stage, detail})` do Bull.

**Fluxo**:

1. Upload retorna `duration` do vídeo.
2. POST `/api/convert` enfileira job com `durationSec`.
3. Worker inicia `convertToAudio()` com `reportProgress` via `job.progress()`.
4. `runWithRealProgress()` faz spawn do FFmpeg, parseia stderr, e emite payloads incrementais.
5. Frontend faz polling em GET `/api/convert/:id` e atualiza barra + timeline.

**Critérios de Aceite**:

- [x] Percent só cresce (monotônico).
- [x] Payload estruturado `{percent, stage, detail}`.
- [x] Thumbnail gerada (5-10%).
- [x] Áudio AAC 128k/44.1k + faststart.
- [x] Fallback silencioso se telemetria falhar.

**Impacto por Camada**:

- Backend: `services/convert.js` (core), `src/routes/convert.js` (rota)
- Worker: `queue/worker.js` (orquestração)
- Frontend: `public/index.html` (UI generativa)

---

### B. Snippet: `runWithRealProgress`

**ID Mestre:** 06022-191500  
**Tags:** `PROG:stderr-parsing`, `PARS:regex-time`, `RESIL:safe-report`  
**Módulo sugerido:** `services/ffmpegProgress.js`

**Assinatura**:

```js
export async function runWithRealProgress(
  args,
  { durationSec, rangeStart, rangeEnd, stage, detail, reportProgress }
) → Promise<void>
```

**Parâmetros**:

| Param            | Tipo     | Default | Descrição                                                      |
| ---------------- | -------- | ------- | -------------------------------------------------------------- |
| `args`           | string[] | —       | Array de argumentos do comando (ex.: `[ffmpegBin, '-i', ...]`) |
| `durationSec`    | number   | 0       | Duração total do vídeo em segundos                             |
| `rangeStart`     | number   | 0       | Percentual inicial da faixa                                    |
| `rangeEnd`       | number   | 95      | Percentual final da faixa                                      |
| `stage`          | string   | —       | Identificador do estágio atual                                 |
| `detail`         | string   | —       | Texto descritivo para o usuário                                |
| `reportProgress` | function | —       | `async ({percent, stage, detail}) → void`                      |

**Código de Referência** (extraído de `backend/services/convert.js`):

```js
const parseTimeFromStderr = (data) => {
  const match = data.match(/time=(\d+):(\d+):(\d+)\.(\d+)/);
  if (!match) return null;
  return (
    parseInt(match[1], 10) * 3600 +
    parseInt(match[2], 10) * 60 +
    parseInt(match[3], 10) +
    parseInt(match[4], 10) / 100
  );
};

const runWithRealProgress = (
  args,
  {
    durationSec = 0,
    rangeStart = 0,
    rangeEnd = 95,
    stage,
    detail,
    reportProgress,
  },
) =>
  new Promise((resolve, reject) => {
    let lastReportedPercent = rangeStart;
    const child = spawn(args[0], args.slice(1), {
      stdio: ["ignore", "pipe", "pipe"],
    });
    const onData = async (chunk) => {
      if (!reportProgress || durationSec <= 0) return;
      const currentTime = parseTimeFromStderr(chunk.toString());
      if (currentTime === null) return;
      const ratio = Math.min(currentTime / durationSec, 1);
      const percent = Math.min(
        Math.floor(rangeStart + ratio * (rangeEnd - rangeStart)),
        rangeEnd,
      );
      if (percent > lastReportedPercent) {
        lastReportedPercent = percent;
        try {
          await reportProgress({
            percent,
            stage,
            detail: `${detail} — ${formatTime(currentTime)}/${formatTime(durationSec)}`,
          });
        } catch (_) {}
      }
    };
    child.stderr.on("data", onData);
    child.stdout.on("data", onData);
    child.on("error", reject);
    child.on("exit", (code) => {
      if (reportProgress)
        reportProgress({
          percent: rangeEnd,
          stage,
          detail: `${detail} — finalizado`,
        }).catch(() => {});
      code === 0
        ? resolve()
        : reject(new Error(`${args[0]} exited with code ${code}`));
    });
  });
```

**Grafo**:

```markdown
worker.js → convertToAudio() → runWithRealProgress()
↓ usa
parseTimeFromStderr()
↓ depende
config.ffmpegBin
```

---

### C. Guia de Adoção: Progresso Real FFmpeg

**ID Mestre:** 06022-191500  
**Projeto de origem:** `aiob3/video2plaud`

**Pré-requisitos**:

- [x] Node ≥ 18 (ESM nativo)
- [x] `type: "module"` no `package.json`
- [x] Bull + ioredis (`npm i bull ioredis`)
- [x] Redis em execução
- [x] FFmpeg/FFprobe no PATH ou em `FFMPEG_BIN`/`FFPROBE_BIN`

**Passos de integração**:

1. Copiar `runWithRealProgress` e `parseTimeFromStderr` para `services/ffmpegProgress.js`.
2. Importar em `services/convert.js` com `import { runWithRealProgress } from './ffmpegProgress.js'`.
3. No worker, garantir que o payload inclua `durationSec` (obtido via ffprobe no upload).
4. Na rota GET `/convert/:id`, extrair `percent`, `stage`, `detail` do `job.progress()`.
5. No frontend, implementar polling com intervalo ~600ms e atualizar UI.

**Testes de validação**:

```bash
# 1. Subir Redis
docker compose up -d redis

# 2. Upload de vídeo de teste (h264, ≥1280x720, <2h)
curl -F "file=@video_teste.mp4" http://localhost:3001/api/upload

# 3. Iniciar conversão (usar path e duration retornados)
curl -X POST -H "Content-Type: application/json" \
  -d '{"path":"/app/uploads/temp/xxx.mp4","title":"teste.mp4","duration":120.5}' \
  http://localhost:3001/api/convert

# 4. Acompanhar progresso (jobId retornado)
watch -n 0.5 'curl -s http://localhost:3001/api/convert/1 | jq .'

# 5. Download
curl -O http://localhost:3001/api/download/1
```

**Troubleshooting**:

| Sintoma                         | Causa provável             | Solução                                                       |
| ------------------------------- | -------------------------- | ------------------------------------------------------------- |
| Progresso trava em `rangeStart` | stderr não contém `time=`  | Verificar codec; FFmpeg pode não emitir para certos formatos  |
| Percent pula de 11% para 95%    | Vídeo muito curto (<5s)    | Normal; poucos chunks de stderr                               |
| `job.progress()` retorna `0`    | Payload não é objeto       | Verificar se `reportProgress` recebe `{percent,stage,detail}` |
| FFmpeg `exited with code 1`     | Codec/formato incompatível | Verificar logs do stderr; validar no upload                   |

→ Ver: Feature Spec "Progresso Real 1-a-1" (ID: 06022-191500)  
→ Ver: Snippet `runWithRealProgress` (ID: 06022-191500)

---

## Formato da resposta (obrigatório)

- **Resumo executivo** em até 6 linhas.
- **Mapa de meios necessários** (lista fechada, tabela 5 colunas).
- **Insights extraídos** (bullet points, cada um com "Por que", "Onde", "Limites").
- **Tríade de artefatos** pronta para publicação (usando os Templates A/B/C).
- **Score da auto-avaliação logarítmica** (tabela L0-L5).
- **Checklist final** (8 itens).

## Regras de qualidade

- Use linguagem objetiva, sem jargões vazios.
- Priorize reutilização e componentização.
- Não "inventar" dependências: se não houver referência, marque como "a confirmar".
- Evite mudanças de escopo; registre novas ideias em "Próximos passos".
- **Toda função extraída deve ser pure ou ter side-effects explicitamente documentados.**
- **Todo snippet deve incluir grafo de dependências.**

## Critérios de aceite

- Saídas completas conforme a tríade.
- Rastreabilidade clara para o documento-base.
- IDs e convenções do projeto respeitados.
- Score ≥ 80/100 na auto-avaliação logarítmica.
- Loop metacognitivo executado (mínimo 1 iteração de scoring).

## Observações

- Se faltar duração, codec ou metadados críticos, solicite ao operador antes de concluir.
- Caso o documento-base esteja incompleto, inferir somente o que for sustentado por evidências.
- **Máximo de 3 iterações do loop para evitar overhead.**
- **Registrar score de cada iteração para auditoria.**

---

## Scoring Final — Instância de Referência

Avaliação após aplicação do protocolo contra `feature-recurso-progressbar.md`:

| Nível     | Aspecto               | Cobertura | Peso | Contribuição |
| --------- | --------------------- | --------- | ---- | ------------ |
| L0        | Existência            | 100%      | 5%   | 5.0          |
| L1        | Estrutura Declarativa | 100%      | 15%  | 15.0         |
| L2        | Schema Formal         | 100%      | 20%  | 20.0         |
| L3        | Instanciação          | 100%      | 25%  | 25.0         |
| L4        | Rastreabilidade       | 90%       | 15%  | 13.5         |
| L5        | Metacognição          | 85%       | 20%  | 17.0         |
| **Total** |                       |           |      | **95.5/100** |

**Status: APROVADO** — Pronto para publicação e importação por projetos derivados.
