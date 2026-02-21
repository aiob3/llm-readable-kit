# Workspace Agent Rules (HITL + Memora)

## Mandatory policy
1. Operator is the final decision authority (HITL).
2. Start Memora logging at the first prompt of every new conversation.
3. Record checkpoints, inferences, decisions, code changes, and deliveries.
4. Every record must include `section` and `atomic_factor` for human-readable correlation.
5. Use only the atomic/idempotent logger:
   - `python3 .agentic/scripts/memora_ops.py ...`

## Required protocol
- Source of truth: `.agentic/MEMORA-PERSISTENT-PROTOCOL.md`

Minimum lifecycle per session:
1. `start`
2. `checkpoint` and `change` during work
3. `inference` and/or `decision` for uncertainty and trade-offs
4. `delivery`
5. `end`

## Operator visibility
- Graph UI: `http://127.0.0.1:8765/graph`
- Event status:
```bash
python3 .agentic/scripts/memora_ops.py status
```
- Correlate legacy records:
```bash
python3 .agentic/scripts/memora_ops.py correlate --report-path .agentic/memora-human-readable-index.md
```
