#!/usr/bin/env python3
"""Backfill typed crossrefs for Memora from action correlations SSOT.

Reads memora_docs/index_graphs_parte2.md (JSON payload) and upserts
memories_crossrefs entries for action_001..action_020 mapped to memory IDs.

Idempotency model:
- For each (from_id, to_id), replace existing ref and write deterministic payload.
- Re-running script produces stable state and zero net changes when already aligned.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB = ROOT / ".opencode" / "memory" / "memoria.db"
DEFAULT_SOURCE = ROOT / "memora_docs" / "index_graphs_parte2.md"


@dataclass(frozen=True)
class Correlation:
    from_id: int
    to_id: int
    edge_type: str
    certainty: float


def action_to_memory_id(action_id: str) -> int:
    # action_001 -> 8 ; action_020 -> 27
    suffix = action_id.split("_")[-1]
    return int(suffix) + 7


def load_correlations(source: Path) -> list[Correlation]:
    raw = source.read_text(encoding="utf-8")
    start = raw.find("{")
    if start < 0:
        raise ValueError(f"Could not find JSON object in {source}")

    payload = json.loads(raw[start:])
    out: list[Correlation] = []

    for item in payload.get("action_correlations", []):
        from_id = action_to_memory_id(item["action_id"])
        for rel in item.get("correlates_to", []):
            to_id = action_to_memory_id(rel["target_action_id"])
            edge_type = str(rel["correlation_type"]).strip()
            certainty = float(rel.get("certainty", 1.0))
            out.append(
                Correlation(
                    from_id=from_id,
                    to_id=to_id,
                    edge_type=edge_type,
                    certainty=certainty,
                )
            )

    return out


def get_crossrefs(conn: sqlite3.Connection, memory_id: int) -> list[dict[str, Any]]:
    row = conn.execute(
        "SELECT related FROM memories_crossrefs WHERE memory_id = ?",
        (memory_id,),
    ).fetchone()
    if not row or not row[0]:
        return []
    try:
        data = json.loads(row[0])
    except Exception:
        return []
    if not isinstance(data, list):
        return []
    return [item for item in data if isinstance(item, dict)]


def memory_exists(conn: sqlite3.Connection, memory_id: int) -> bool:
    row = conn.execute("SELECT 1 FROM memories WHERE id=?", (memory_id,)).fetchone()
    return row is not None


def normalize_refs(refs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    # deterministic ordering by target id then edge_type
    return sorted(
        refs,
        key=lambda r: (int(r.get("id", -1)), str(r.get("edge_type", ""))),
    )


def upsert_crossrefs(conn: sqlite3.Connection, memory_id: int, refs: list[dict[str, Any]]) -> None:
    related_json = json.dumps(normalize_refs(refs), ensure_ascii=False)
    conn.execute(
        """
        INSERT INTO memories_crossrefs(memory_id, related)
        VALUES (?, ?)
        ON CONFLICT(memory_id) DO UPDATE SET related=excluded.related
        """,
        (memory_id, related_json),
    )


def apply_backfill(db_path: Path, correlations: list[Correlation]) -> dict[str, Any]:
    conn = sqlite3.connect(db_path)

    updated_from_ids: set[int] = set()
    replaced_edges = 0
    inserted_edges = 0
    unchanged_edges = 0
    skipped_missing: list[tuple[int, int]] = []

    try:
        conn.execute("BEGIN IMMEDIATE")

        grouped: dict[int, list[Correlation]] = {}
        for c in correlations:
            grouped.setdefault(c.from_id, []).append(c)

        for from_id, rels in grouped.items():
            if not memory_exists(conn, from_id):
                skipped_missing.extend((from_id, c.to_id) for c in rels)
                continue

            refs = get_crossrefs(conn, from_id)
            existing_by_target = {int(r.get("id", -1)): r for r in refs if "id" in r}
            kept = [r for r in refs if int(r.get("id", -1)) not in {c.to_id for c in rels}]
            changed = False

            for c in rels:
                if not memory_exists(conn, c.to_id):
                    skipped_missing.append((c.from_id, c.to_id))
                    continue

                prev = existing_by_target.get(c.to_id)
                new_entry = {
                    "id": c.to_id,
                    "score": c.certainty,
                    "edge_type": c.edge_type,
                    "certainty": c.certainty,
                    "source": "index_graphs_parte2_backfill_2026-02-21",
                }

                if prev is None:
                    inserted_edges += 1
                    changed = True
                else:
                    prev_norm = {
                        "id": int(prev.get("id", -1)),
                        "score": float(prev.get("score", 0)),
                        "edge_type": str(prev.get("edge_type", "")),
                        "certainty": float(prev.get("certainty", prev.get("score", 0))),
                        "source": str(prev.get("source", "")),
                    }
                    if prev_norm != new_entry:
                        replaced_edges += 1
                        changed = True
                    else:
                        unchanged_edges += 1

                kept.append(new_entry)

            if changed:
                upsert_crossrefs(conn, from_id, kept)
                updated_from_ids.add(from_id)

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    return {
        "status": "ok",
        "total_correlations_input": len(correlations),
        "from_nodes_updated": len(updated_from_ids),
        "inserted_edges": inserted_edges,
        "replaced_edges": replaced_edges,
        "unchanged_edges": unchanged_edges,
        "skipped_missing": skipped_missing,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Backfill Memora typed edges from action correlation SSOT")
    parser.add_argument("--db-path", default=str(DEFAULT_DB))
    parser.add_argument("--source", default=str(DEFAULT_SOURCE))
    args = parser.parse_args()

    db_path = Path(args.db_path)
    source = Path(args.source)

    correlations = load_correlations(source)
    result = apply_backfill(db_path, correlations)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
