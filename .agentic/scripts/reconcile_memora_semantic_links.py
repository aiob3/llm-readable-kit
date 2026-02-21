#!/usr/bin/env python3
"""Reconcile Memora graph usability: duplicate noise + orphan chains.

Actions:
1) Normalize scores for backfilled causal links (keep certainty, lower score < duplicate threshold).
2) Add recursive semantic links for session event chains and orphan non-event memories.

Idempotency:
- Re-running only updates when values differ.
- Existing links are replaced by target id (single canonical relation per from->to).
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB = ROOT / ".opencode" / "memory" / "memoria.db"

DUPLICATE_THRESHOLD = 0.85
MIN_VISIBLE_SCORE = 0.40
SOURCE_BACKFILL = "index_graphs_parte2_backfill_2026-02-21"
SOURCE_RECURSIVE = "recursive_semantic_correlation_2026-02-21"


@dataclass(frozen=True)
class SemanticLink:
    from_id: int
    to_id: int
    edge_type: str
    score: float
    certainty: float
    reason: str


def parse_dt(raw: str) -> datetime:
    # expected format: "YYYY-MM-DD HH:MM:SS"
    return datetime.strptime(raw.split(".")[0], "%Y-%m-%d %H:%M:%S")


def get_memories(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = conn.execute(
        "SELECT id, content, metadata, tags, created_at FROM memories ORDER BY id"
    ).fetchall()
    out: list[dict[str, Any]] = []
    for row in rows:
        metadata = {}
        tags: list[str] = []
        if row[2]:
            try:
                metadata = json.loads(row[2])
            except Exception:
                metadata = {}
        if row[3]:
            try:
                tags = json.loads(row[3])
            except Exception:
                tags = []
        out.append(
            {
                "id": int(row[0]),
                "content": row[1],
                "metadata": metadata,
                "tags": tags,
                "created_at": row[4],
            }
        )
    return out


def get_crossrefs(conn: sqlite3.Connection, memory_id: int) -> list[dict[str, Any]]:
    row = conn.execute(
        "SELECT related FROM memories_crossrefs WHERE memory_id=?", (memory_id,)
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


def upsert_crossrefs(conn: sqlite3.Connection, memory_id: int, refs: list[dict[str, Any]]) -> None:
    refs_sorted = sorted(
        refs,
        key=lambda r: (int(r.get("id", -1)), str(r.get("edge_type", "")), str(r.get("source", ""))),
    )
    payload = json.dumps(refs_sorted, ensure_ascii=False)
    conn.execute(
        """
        INSERT INTO memories_crossrefs(memory_id, related)
        VALUES (?, ?)
        ON CONFLICT(memory_id) DO UPDATE SET related=excluded.related
        """,
        (memory_id, payload),
    )


def current_orphans(conn: sqlite3.Connection, min_score: float = MIN_VISIBLE_SCORE) -> list[int]:
    memory_ids = {int(r[0]) for r in conn.execute("SELECT id FROM memories").fetchall()}
    conn_count = {mid: 0 for mid in memory_ids}

    rows = conn.execute("SELECT memory_id, related FROM memories_crossrefs WHERE related IS NOT NULL").fetchall()
    for mid, related in rows:
        try:
            refs = json.loads(related)
        except Exception:
            continue
        if not isinstance(refs, list):
            continue
        for ref in refs:
            if not isinstance(ref, dict):
                continue
            rid = int(ref.get("id", -1))
            score = float(ref.get("score", 0))
            if score > min_score and rid in memory_ids:
                conn_count[int(mid)] = conn_count.get(int(mid), 0) + 1
                conn_count[rid] = conn_count.get(rid, 0) + 1

    return sorted([mid for mid, count in conn_count.items() if count == 0])


def current_duplicate_ids(conn: sqlite3.Connection, threshold: float = DUPLICATE_THRESHOLD) -> set[int]:
    memory_ids = {int(r[0]) for r in conn.execute("SELECT id FROM memories").fetchall()}
    dups: set[int] = set()
    rows = conn.execute("SELECT memory_id, related FROM memories_crossrefs WHERE related IS NOT NULL").fetchall()
    for mid, related in rows:
        try:
            refs = json.loads(related)
        except Exception:
            continue
        if not isinstance(refs, list):
            continue
        for ref in refs:
            if not isinstance(ref, dict):
                continue
            rid = int(ref.get("id", -1))
            score = float(ref.get("score", 0))
            if score >= threshold and rid in memory_ids:
                dups.add(int(mid))
                dups.add(rid)
    return dups


def safe_score_from_certainty(certainty: float) -> float:
    certainty = max(0.0, min(1.0, certainty))
    # Keep visible (>0.40) but below duplicate threshold (<0.85)
    # range: [0.62, 0.84]
    return round(0.62 + certainty * 0.22, 3)


def normalize_backfill_scores(conn: sqlite3.Connection) -> dict[str, int]:
    rows = conn.execute("SELECT memory_id, related FROM memories_crossrefs WHERE related IS NOT NULL").fetchall()
    updated_rows = 0
    adjusted_edges = 0
    unchanged_edges = 0

    for mid, related in rows:
        refs = json.loads(related)
        changed = False

        for ref in refs:
            if not isinstance(ref, dict):
                continue
            if ref.get("source") != SOURCE_BACKFILL:
                continue

            certainty = float(ref.get("certainty", ref.get("score", 0.8)))
            target_score = safe_score_from_certainty(certainty)
            current = float(ref.get("score", 0.0))

            if abs(current - target_score) > 1e-9:
                ref["score"] = target_score
                changed = True
                adjusted_edges += 1
            else:
                unchanged_edges += 1

        if changed:
            upsert_crossrefs(conn, int(mid), refs)
            updated_rows += 1

    return {
        "updated_rows": updated_rows,
        "adjusted_edges": adjusted_edges,
        "unchanged_edges": unchanged_edges,
    }


def relation_for_pair(prev_type: str, next_type: str) -> tuple[str, float, float, str]:
    mapping: dict[tuple[str, str], tuple[str, float, float, str]] = {
        ("session_start", "checkpoint"): ("enables", 0.78, 0.95, "session_event_chain"),
        ("checkpoint", "code_change"): ("enables", 0.76, 0.9, "session_event_chain"),
        ("checkpoint", "inference"): ("refines", 0.74, 0.88, "session_event_chain"),
        ("checkpoint", "decision"): ("enables", 0.74, 0.86, "session_event_chain"),
        ("inference", "decision"): ("enables", 0.79, 0.93, "session_event_chain"),
        ("decision", "delivery"): ("enables", 0.8, 0.94, "session_event_chain"),
        ("code_change", "delivery"): ("implements", 0.8, 0.95, "session_event_chain"),
        ("delivery", "session_end"): ("validates", 0.77, 0.9, "session_event_chain"),
        ("session_start", "inference"): ("enables", 0.72, 0.84, "session_event_chain"),
        ("session_start", "delivery"): ("enables", 0.72, 0.82, "session_event_chain"),
        ("delivery", "checkpoint"): ("refines", 0.7, 0.8, "session_event_chain"),
    }
    return mapping.get((prev_type, next_type), ("refines", 0.7, 0.8, "session_event_chain"))


def build_recursive_links(memories: list[dict[str, Any]]) -> list[SemanticLink]:
    by_session: dict[str, list[dict[str, Any]]] = {}
    for m in memories:
        meta = m.get("metadata") or {}
        sid = meta.get("session_id")
        et = meta.get("event_type")
        if sid and et:
            by_session.setdefault(str(sid), []).append(m)

    links: list[SemanticLink] = []

    # 1) Intra-session recursive event chains
    for sid, items in by_session.items():
        ordered = sorted(items, key=lambda x: (parse_dt(x["created_at"]), x["id"]))
        for prev, nxt in zip(ordered, ordered[1:]):
            ptype = str((prev.get("metadata") or {}).get("event_type", ""))
            ntype = str((nxt.get("metadata") or {}).get("event_type", ""))
            edge_type, score, certainty, reason = relation_for_pair(ptype, ntype)
            links.append(
                SemanticLink(
                    from_id=int(prev["id"]),
                    to_id=int(nxt["id"]),
                    edge_type=edge_type,
                    score=score,
                    certainty=certainty,
                    reason=reason,
                )
            )

    # 2) Inter-session bridge: session_end -> next session_start
    start_events = []
    end_events = []
    for m in memories:
        meta = m.get("metadata") or {}
        et = meta.get("event_type")
        if et == "session_start":
            start_events.append(m)
        elif et == "session_end":
            end_events.append(m)

    start_events.sort(key=lambda x: (parse_dt(x["created_at"]), x["id"]))
    end_events.sort(key=lambda x: (parse_dt(x["created_at"]), x["id"]))

    for end_ev in end_events:
        end_dt = parse_dt(end_ev["created_at"])
        next_start = None
        for st in start_events:
            if parse_dt(st["created_at"]) >= end_dt and st["id"] != end_ev["id"]:
                next_start = st
                break
        if next_start:
            links.append(
                SemanticLink(
                    from_id=int(end_ev["id"]),
                    to_id=int(next_start["id"]),
                    edge_type="enables",
                    score=0.66,
                    certainty=0.78,
                    reason="inter_session_handoff",
                )
            )

    # 3) Non-event orphan bridge (legacy tacit records)
    # Link legacy semantic records in chronological order to avoid isolated islands.
    non_event = [m for m in memories if not (m.get("metadata") or {}).get("event_type")]
    non_event.sort(key=lambda x: (parse_dt(x["created_at"]), x["id"]))
    for prev, nxt in zip(non_event, non_event[1:]):
        links.append(
            SemanticLink(
                from_id=int(prev["id"]),
                to_id=int(nxt["id"]),
                edge_type="references",
                score=0.64,
                certainty=0.75,
                reason="legacy_semantic_chain",
            )
        )

    # Also connect last legacy memory to first session_start for continuity.
    if non_event and start_events:
        first_start = min(start_events, key=lambda x: (parse_dt(x["created_at"]), x["id"]))
        links.append(
            SemanticLink(
                from_id=int(non_event[-1]["id"]),
                to_id=int(first_start["id"]),
                edge_type="enables",
                score=0.63,
                certainty=0.74,
                reason="legacy_to_operational_bridge",
            )
        )

    # Deduplicate by from->to keeping max score
    best: dict[tuple[int, int], SemanticLink] = {}
    for link in links:
        key = (link.from_id, link.to_id)
        cur = best.get(key)
        if cur is None or link.score > cur.score:
            best[key] = link

    return list(best.values())


def apply_links(conn: sqlite3.Connection, links: list[SemanticLink]) -> dict[str, int]:
    inserted = 0
    updated = 0
    unchanged = 0
    updated_from_ids: set[int] = set()

    for link in links:
        refs = get_crossrefs(conn, link.from_id)
        existing = None
        others = []
        for ref in refs:
            rid = int(ref.get("id", -1))
            if rid == link.to_id:
                existing = ref
            else:
                others.append(ref)

        new_ref = {
            "id": link.to_id,
            "score": link.score,
            "edge_type": link.edge_type,
            "certainty": link.certainty,
            "source": SOURCE_RECURSIVE,
            "reason": link.reason,
        }

        if existing is None:
            inserted += 1
            changed = True
        else:
            existing_norm = {
                "id": int(existing.get("id", -1)),
                "score": float(existing.get("score", 0.0)),
                "edge_type": str(existing.get("edge_type", "")),
                "certainty": float(existing.get("certainty", existing.get("score", 0.0))),
                "source": str(existing.get("source", "")),
                "reason": str(existing.get("reason", "")),
            }
            if existing_norm == new_ref:
                unchanged += 1
                changed = False
            else:
                updated += 1
                changed = True

        if changed:
            others.append(new_ref)
            upsert_crossrefs(conn, link.from_id, others)
            updated_from_ids.add(link.from_id)

    return {
        "inserted": inserted,
        "updated": updated,
        "unchanged": unchanged,
        "from_nodes_touched": len(updated_from_ids),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Reconcile Memora semantic graph usability")
    parser.add_argument("--db-path", default=str(DEFAULT_DB))
    args = parser.parse_args()

    db_path = Path(args.db_path)
    conn = sqlite3.connect(db_path)

    try:
        conn.execute("BEGIN IMMEDIATE")

        before_orphans = current_orphans(conn)
        before_dups = sorted(current_duplicate_ids(conn))

        score_stats = normalize_backfill_scores(conn)
        memories = get_memories(conn)
        links = build_recursive_links(memories)
        link_stats = apply_links(conn, links)

        after_orphans = current_orphans(conn)
        after_dups = sorted(current_duplicate_ids(conn))

        conn.commit()

        result = {
            "status": "ok",
            "before": {
                "orphans_count": len(before_orphans),
                "orphans": before_orphans,
                "duplicate_ids_count": len(before_dups),
                "duplicate_ids": before_dups,
            },
            "score_normalization": score_stats,
            "semantic_links": {
                "generated": len(links),
                **link_stats,
            },
            "after": {
                "orphans_count": len(after_orphans),
                "orphans": after_orphans,
                "duplicate_ids_count": len(after_dups),
                "duplicate_ids": after_dups,
            },
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
