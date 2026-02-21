#!/usr/bin/env python3
"""Reorder Memora tags to improve graph coloring by semantic primary tag.

Memora graph uses first tag as color key. This script promotes semantic tags:
1) section:*
2) atomic:*
3) event tags (session-start/checkpoint/code-change/inference/decision/delivery/session-end)
4) other non-generic tags
5) generic tags (agentic, memora, hitl, ...)

Idempotent: re-running preserves stable order.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB = ROOT / ".opencode" / "memory" / "memoria.db"

GENERIC = {
    "agentic",
    "memora",
    "hitl",
    "tracking",
    "implementation",
    "metacognition",
    "pareto",
    "codex",
}

EVENT_TAGS = {
    "session-start",
    "checkpoint",
    "code-change",
    "inference",
    "decision",
    "delivery",
    "session-end",
}


def reorder(tags: list[str]) -> list[str]:
    # stable unique
    uniq = []
    seen = set()
    for t in tags:
        if t not in seen:
            uniq.append(t)
            seen.add(t)

    sec = [t for t in uniq if t.startswith("section:")]
    atomic = [t for t in uniq if t.startswith("atomic:")]
    event = [t for t in uniq if t in EVENT_TAGS]
    other = [
        t
        for t in uniq
        if t not in sec and t not in atomic and t not in event and t not in GENERIC
    ]
    generic = [t for t in uniq if t in GENERIC]

    return sec + atomic + event + other + generic


def main() -> None:
    parser = argparse.ArgumentParser(description="Reorder Memora tags for semantic coloring")
    parser.add_argument("--db-path", default=str(DEFAULT_DB))
    args = parser.parse_args()

    conn = sqlite3.connect(Path(args.db_path))
    cur = conn.cursor()

    before_first = Counter()
    after_first = Counter()
    updated = 0

    try:
        conn.execute("BEGIN IMMEDIATE")
        rows = cur.execute("SELECT id, tags, content, metadata FROM memories").fetchall()

        for mid, tags_json, content, metadata in rows:
            tags = []
            if tags_json:
                try:
                    tags = json.loads(tags_json)
                except Exception:
                    tags = []

            if tags:
                before_first[tags[0]] += 1

            new_tags = reorder(tags)
            if new_tags:
                after_first[new_tags[0]] += 1

            if new_tags != tags:
                cur.execute(
                    "UPDATE memories SET tags=? WHERE id=?",
                    (json.dumps(new_tags, ensure_ascii=False), mid),
                )
                if conn.execute(
                    "SELECT 1 FROM sqlite_master WHERE type='table' AND name='memories_fts'"
                ).fetchone():
                    cur.execute(
                        "INSERT OR REPLACE INTO memories_fts(rowid, content, metadata, tags) VALUES (?, ?, ?, ?)",
                        (
                            mid,
                            content,
                            metadata,
                            json.dumps(new_tags, ensure_ascii=False),
                        ),
                    )
                updated += 1

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    print(
        json.dumps(
            {
                "status": "ok",
                "updated_rows": updated,
                "before_top_first": before_first.most_common(10),
                "after_top_first": after_first.most_common(10),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
