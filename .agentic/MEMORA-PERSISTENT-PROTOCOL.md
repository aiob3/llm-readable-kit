# Memora Persistent Protocol (HITL)

## Purpose
Guarantee that every agent interaction in this workspace registers progress in Memora from the first prompt of a new conversation, with operator visibility and restart continuity.

## Mandatory Rules
1. Operator authority is final (HITL).
2. Any meaningful step must be registered in Memora.
3. Use atomic and idempotent registration via `.agentic/scripts/memora_ops.py`.
4. Categorize each event with `section` and `atomic_factor`.
5. If there is uncertainty, record inference + decision alternatives before acting.

## Session Lifecycle (Mandatory)

### 1) Start (first prompt of each new conversation)
```bash
python3 .agentic/scripts/memora_ops.py start \
  --agent codex \
  --operator operador \
  --objective "<objetivo da conversa>" \
  --prompt-summary "<resumo do primeiro prompt>" \
  --section "governance/session" \
  --atomic-factor "session-lifecycle"
```

### 2) During work (repeat as needed)
- Checkpoint:
```bash
python3 .agentic/scripts/memora_ops.py checkpoint \
  --title "<marco>" \
  --summary "<o que foi feito>" \
  --files "arquivo1,arquivo2" \
  --effort low|medium|high \
  --impact low|medium|high \
  --pareto "80/20" \
  --next-step "<proximo passo>" \
  --section "delivery/checkpoint" \
  --atomic-factor "milestone-tracking"
```

- Code change:
```bash
python3 .agentic/scripts/memora_ops.py change \
  --summary "<mudanca aplicada>" \
  --files "arquivo1,arquivo2" \
  --tests "<resultado de testes>" \
  --result "<status>" \
  --section "implementation/code" \
  --atomic-factor "code-delta"
```

- Metacognitive inference:
```bash
python3 .agentic/scripts/memora_ops.py inference \
  --hypothesis "<hipotese>" \
  --evidence "<evidencias>" \
  --uncertainty "<incerteza>" \
  --mitigation "<mitigacao proposta>" \
  --section "analysis/inference" \
  --atomic-factor "uncertainty-mitigation"
```

- Decision with alternatives:
```bash
python3 .agentic/scripts/memora_ops.py decision \
  --question "<decisao a tomar>" \
  --options "opcao-a,opcao-b,opcao-c" \
  --selected "<opcao escolhida>" \
  --rationale "<justificativa>" \
  --effort low|medium|high \
  --impact low|medium|high \
  --pareto "80/20" \
  --section "analysis/decision" \
  --atomic-factor "tradeoff-resolution"
```

### 3) Delivery and end
```bash
python3 .agentic/scripts/memora_ops.py delivery \
  --summary "<entrega consolidada>" \
  --artifacts "arquivo1,arquivo2" \
  --verification "<evidencia de validacao>" \
  --section "delivery/release" \
  --atomic-factor "artifact-verification"
```

```bash
python3 .agentic/scripts/memora_ops.py end \
  --summary "<resumo final>" \
  --next-steps "<pendencias e proximos passos>" \
  --section "governance/session" \
  --atomic-factor "session-lifecycle"
```

## Atomicity and Idempotency Design
- Atomicity: single SQLite transaction (`BEGIN IMMEDIATE`) for dedupe + write + registry update.
- Idempotency: deterministic `event_key` based on event_type + session_id + payload hash.
- Replay-safe: repeated command with same payload returns existing `memory_id` and does not duplicate.
- Traceability: `agentic_event_registry` table links `event_key -> memory_id`.
- Human-readable correlation: `agentic_section_registry` links `human_ref -> section -> atomic_factor -> event`.

## Operator Visibility
- Graph UI: `http://127.0.0.1:8765/graph`
- Event status:
```bash
python3 .agentic/scripts/memora_ops.py status
```

Backfill existing registros sem section/human_ref:
```bash
python3 .agentic/scripts/memora_ops.py correlate \
  --report-path .agentic/memora-human-readable-index.md
```

## SSOT Canonical Operations (v1)
- Hard reset (destrutivo, exige token explicito):
```bash
python3 .agentic/scripts/memora_ops.py reset-hard --confirm RESET-YES
```

- Ingestao canônica idempotente (DSL -> segmentos atomicos):
```bash
python3 .agentic/scripts/memora_ops.py canonical-ingest \
  --dsl .agentic/canonical/bootstrap.dsl \
  --session-id "<session_id>" \
  --session-state start
```

- Recompute de clusters (sessao master):
```bash
python3 .agentic/scripts/memora_ops.py recompute-clusters --mode session-master
```

- Verificacao de integridade (idempotencia, orfaos, politica de duplicates):
```bash
python3 .agentic/scripts/memora_ops.py verify-integrity --strict
```

## Agent Compliance
Any agent working in this workspace must treat this protocol as default behavior for all coding-related activities.
