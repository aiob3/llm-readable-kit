#!/usr/bin/env python3
"""Atomic and idempotent Memora operation logger for workspace agents.

This utility is designed to be called from any agent workflow to ensure
persistent visibility of progress for HITL operation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB = ROOT / ".opencode" / "memory" / "memoria.db"
ACTIVE_SESSION_FILE = ROOT / ".agentic" / "active-session.json"
DEFAULT_REPORT_PATH = ROOT / ".agentic" / "memora-human-readable-index.md"


def utc_now_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def canonical_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def make_session_id(agent: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    token = hashlib.sha256(f"{agent}:{stamp}".encode("utf-8")).hexdigest()[:8]
    return f"{stamp}-{agent}-{token}"


def make_event_key(event_type: str, session_id: str, payload: dict[str, Any]) -> str:
    payload_hash = hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()
    return f"{event_type}:{session_id}:{payload_hash[:24]}"


def parse_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def load_active_session() -> dict[str, Any] | None:
    if not ACTIVE_SESSION_FILE.exists():
        return None
    try:
        return json.loads(ACTIVE_SESSION_FILE.read_text(encoding="utf-8"))
    except Exception:
        return None


def save_active_session(data: dict[str, Any]) -> None:
    ensure_parent(ACTIVE_SESSION_FILE)
    ACTIVE_SESSION_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def clear_active_session() -> None:
    if ACTIVE_SESSION_FILE.exists():
        ACTIVE_SESSION_FILE.unlink()


def sanitize_token(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9/_-]+", "-", value.strip())
    cleaned = re.sub(r"-+", "-", cleaned).strip("-")
    return cleaned.lower() or "uncategorized"


def default_section_for_event(event_type: str) -> str:
    mapping = {
        "session_start": "governance/session",
        "checkpoint": "delivery/checkpoint",
        "code_change": "implementation/code",
        "inference": "analysis/inference",
        "decision": "analysis/decision",
        "delivery": "delivery/release",
        "session_end": "governance/session",
    }
    return mapping.get(event_type, "misc/general")


def default_atomic_factor_for_event(event_type: str) -> str:
    mapping = {
        "session_start": "session-lifecycle",
        "checkpoint": "milestone-tracking",
        "code_change": "code-delta",
        "inference": "uncertainty-mitigation",
        "decision": "tradeoff-resolution",
        "delivery": "artifact-verification",
        "session_end": "session-lifecycle",
    }
    return mapping.get(event_type, "general")


def make_human_ref(section: str, event_type: str, payload_hash: str) -> str:
    sec = sanitize_token(section).replace("/", "-")
    evt = sanitize_token(event_type)
    return f"sec-{sec}-{evt}-{payload_hash[:10]}"


def table_exists(conn: sqlite3.Connection, table: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
        (table,),
    ).fetchone()
    return row is not None


def ensure_agentic_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS agentic_event_registry (
            event_key TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            payload_hash TEXT NOT NULL,
            memory_id INTEGER,
            status TEXT NOT NULL DEFAULT 'applied',
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS agentic_section_registry (
            human_ref TEXT PRIMARY KEY,
            event_key TEXT UNIQUE NOT NULL,
            memory_id INTEGER,
            session_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            section TEXT NOT NULL,
            atomic_factor TEXT NOT NULL,
            payload_hash TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'applied',
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT
        )
        """
    )


def insert_memory_record(
    conn: sqlite3.Connection,
    *,
    content: str,
    metadata: dict[str, Any],
    tags: list[str],
    event_type: str,
    event_key: str,
) -> int:
    created_at = utc_now_str()
    metadata_json = json.dumps(metadata, ensure_ascii=False)
    tags_json = json.dumps(tags, ensure_ascii=False)

    cur = conn.execute(
        "INSERT INTO memories (content, metadata, tags, created_at) VALUES (?, ?, ?, ?)",
        (content, metadata_json, tags_json, created_at),
    )
    memory_id = int(cur.lastrowid)

    if table_exists(conn, "memories_fts"):
        conn.execute(
            "INSERT OR REPLACE INTO memories_fts(rowid, content, metadata, tags) VALUES (?, ?, ?, ?)",
            (memory_id, content, metadata_json, tags_json),
        )

    if table_exists(conn, "memories_actions"):
        conn.execute(
            "INSERT INTO memories_actions (memory_id, action, summary) VALUES (?, ?, ?)",
            (
                memory_id,
                "create",
                f"Agentic event {event_type} registered ({event_key})",
            ),
        )

    return memory_id


def find_memory_by_event_key(conn: sqlite3.Connection, event_key: str) -> int | None:
    row = conn.execute(
        """
        SELECT id
        FROM memories
        WHERE json_extract(metadata, '$.event_key') = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (event_key,),
    ).fetchone()
    return int(row[0]) if row else None


def ensure_tags(tags: list[str], section: str, atomic_factor: str) -> list[str]:
    merged = [*tags, f"section:{sanitize_token(section)}", f"atomic:{sanitize_token(atomic_factor)}"]
    deduped: list[str] = []
    seen: set[str] = set()
    for tag in merged:
        if tag not in seen:
            deduped.append(tag)
            seen.add(tag)
    return deduped


def upsert_section_registry(
    conn: sqlite3.Connection,
    *,
    human_ref: str,
    event_key: str,
    memory_id: int,
    session_id: str,
    event_type: str,
    section: str,
    atomic_factor: str,
    payload_hash: str,
) -> None:
    conn.execute(
        """
        INSERT INTO agentic_section_registry(
            human_ref, event_key, memory_id, session_id, event_type, section, atomic_factor, payload_hash, status, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'applied', ?)
        ON CONFLICT(event_key) DO UPDATE SET
            human_ref=excluded.human_ref,
            memory_id=excluded.memory_id,
            session_id=excluded.session_id,
            event_type=excluded.event_type,
            section=excluded.section,
            atomic_factor=excluded.atomic_factor,
            payload_hash=excluded.payload_hash,
            status='applied',
            updated_at=excluded.updated_at
        """,
        (
            human_ref,
            event_key,
            memory_id,
            session_id,
            event_type,
            section,
            atomic_factor,
            payload_hash,
            utc_now_str(),
        ),
    )


def register_event(
    *,
    db_path: Path,
    session_id: str,
    event_type: str,
    payload: dict[str, Any],
    content: str,
    tags: list[str],
    section: str,
    atomic_factor: str,
) -> dict[str, Any]:
    ensure_parent(db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    payload_hash = hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()
    event_key = make_event_key(event_type, session_id, payload)
    human_ref = make_human_ref(section, event_type, payload_hash)

    try:
        conn.execute("BEGIN IMMEDIATE")
        ensure_agentic_schema(conn)

        existing = conn.execute(
            "SELECT event_key, memory_id, status FROM agentic_event_registry WHERE event_key=?",
            (event_key,),
        ).fetchone()
        if existing and existing["memory_id"]:
            upsert_section_registry(
                conn,
                human_ref=human_ref,
                event_key=event_key,
                memory_id=int(existing["memory_id"]),
                session_id=session_id,
                event_type=event_type,
                section=section,
                atomic_factor=atomic_factor,
                payload_hash=payload_hash,
            )
            conn.commit()
            return {
                "status": "already_exists",
                "event_key": event_key,
                "memory_id": int(existing["memory_id"]),
                "session_id": session_id,
                "event_type": event_type,
                "section": section,
                "atomic_factor": atomic_factor,
                "human_ref": human_ref,
            }

        known_memory_id = find_memory_by_event_key(conn, event_key)
        if known_memory_id:
            conn.execute(
                """
                INSERT INTO agentic_event_registry(event_key, session_id, event_type, payload_hash, memory_id, status, updated_at)
                VALUES (?, ?, ?, ?, ?, 'applied', ?)
                ON CONFLICT(event_key) DO UPDATE SET
                    memory_id=excluded.memory_id,
                    status='applied',
                    payload_hash=excluded.payload_hash,
                    updated_at=excluded.updated_at
                """,
                (event_key, session_id, event_type, payload_hash, known_memory_id, utc_now_str()),
            )
            upsert_section_registry(
                conn,
                human_ref=human_ref,
                event_key=event_key,
                memory_id=known_memory_id,
                session_id=session_id,
                event_type=event_type,
                section=section,
                atomic_factor=atomic_factor,
                payload_hash=payload_hash,
            )
            conn.commit()
            return {
                "status": "already_exists",
                "event_key": event_key,
                "memory_id": known_memory_id,
                "session_id": session_id,
                "event_type": event_type,
                "section": section,
                "atomic_factor": atomic_factor,
                "human_ref": human_ref,
            }

        conn.execute(
            """
            INSERT INTO agentic_event_registry(event_key, session_id, event_type, payload_hash, memory_id, status, updated_at)
            VALUES (?, ?, ?, ?, NULL, 'processing', ?)
            ON CONFLICT(event_key) DO UPDATE SET
                payload_hash=excluded.payload_hash,
                status='processing',
                updated_at=excluded.updated_at
            """,
            (event_key, session_id, event_type, payload_hash, utc_now_str()),
        )

        metadata = dict(payload)
        metadata.update(
            {
                "event_key": event_key,
                "event_type": event_type,
                "session_id": session_id,
                "recorded_at_utc": utc_now_str(),
                "recorded_by": "memora_ops.py",
                "section": section,
                "atomic_factor": atomic_factor,
                "human_ref": human_ref,
            }
        )
        memory_id = insert_memory_record(
            conn,
            content=content,
            metadata=metadata,
            tags=ensure_tags(tags, section, atomic_factor),
            event_type=event_type,
            event_key=event_key,
        )

        conn.execute(
            """
            UPDATE agentic_event_registry
            SET memory_id=?, status='applied', updated_at=?
            WHERE event_key=?
            """,
            (memory_id, utc_now_str(), event_key),
        )

        upsert_section_registry(
            conn,
            human_ref=human_ref,
            event_key=event_key,
            memory_id=memory_id,
            session_id=session_id,
            event_type=event_type,
            section=section,
            atomic_factor=atomic_factor,
            payload_hash=payload_hash,
        )

        conn.commit()
        return {
            "status": "created",
            "event_key": event_key,
            "memory_id": memory_id,
            "session_id": session_id,
            "event_type": event_type,
            "section": section,
            "atomic_factor": atomic_factor,
            "human_ref": human_ref,
        }
    finally:
        conn.close()


def resolve_session_id(args: argparse.Namespace) -> str:
    if args.session_id:
        return args.session_id
    active = load_active_session()
    if not active or not active.get("session_id"):
        raise SystemExit(
            "No active session. Run 'start' first or pass --session-id explicitly."
        )
    return str(active["session_id"])


def resolve_section(args: argparse.Namespace, event_type: str) -> str:
    return sanitize_token(args.section or default_section_for_event(event_type))


def resolve_atomic_factor(args: argparse.Namespace, event_type: str) -> str:
    return sanitize_token(args.atomic_factor or default_atomic_factor_for_event(event_type))


def cmd_start(args: argparse.Namespace) -> None:
    session_id = args.session_id or make_session_id(args.agent)
    section = resolve_section(args, "session_start")
    atomic_factor = resolve_atomic_factor(args, "session_start")
    payload = {
        "agent": args.agent,
        "operator": args.operator,
        "objective": args.objective,
        "prompt_summary": args.prompt_summary,
        "workspace": str(ROOT),
        "mode": "session_start",
        "section": section,
        "atomic_factor": atomic_factor,
    }
    content = (
        f"Session start [{session_id}] section={section} atomic={atomic_factor} "
        f"agent={args.agent}. Objective: {args.objective}. Prompt summary: {args.prompt_summary}."
    )
    tags = ["agentic", "memora", "session-start", args.agent, "hitl"]
    result = register_event(
        db_path=Path(args.db_path),
        session_id=session_id,
        event_type="session_start",
        payload=payload,
        content=content,
        tags=tags,
        section=section,
        atomic_factor=atomic_factor,
    )
    save_active_session(
        {
            "session_id": session_id,
            "agent": args.agent,
            "operator": args.operator,
            "objective": args.objective,
            "started_at_utc": utc_now_str(),
            "start_memory_id": result["memory_id"],
            "section": section,
            "atomic_factor": atomic_factor,
        }
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_checkpoint(args: argparse.Namespace) -> None:
    session_id = resolve_session_id(args)
    section = resolve_section(args, "checkpoint")
    atomic_factor = resolve_atomic_factor(args, "checkpoint")
    files = parse_csv(args.files)
    payload = {
        "title": args.title,
        "summary": args.summary,
        "files": files,
        "effort": args.effort,
        "impact": args.impact,
        "pareto": args.pareto,
        "next_step": args.next_step,
        "section": section,
        "atomic_factor": atomic_factor,
    }
    content = (
        f"Checkpoint [{session_id}] section={section} atomic={atomic_factor} {args.title}. {args.summary}. "
        f"Effort={args.effort}; Impact={args.impact}; Pareto={args.pareto}. "
        f"Next step: {args.next_step}."
    )
    tags = ["agentic", "memora", "checkpoint", "hitl", "tracking"]
    result = register_event(
        db_path=Path(args.db_path),
        session_id=session_id,
        event_type="checkpoint",
        payload=payload,
        content=content,
        tags=tags,
        section=section,
        atomic_factor=atomic_factor,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_change(args: argparse.Namespace) -> None:
    session_id = resolve_session_id(args)
    section = resolve_section(args, "code_change")
    atomic_factor = resolve_atomic_factor(args, "code_change")
    files = parse_csv(args.files)
    payload = {
        "summary": args.summary,
        "files": files,
        "tests": args.tests,
        "result": args.result,
        "section": section,
        "atomic_factor": atomic_factor,
    }
    content = (
        f"Code change [{session_id}] section={section} atomic={atomic_factor}: {args.summary}. "
        f"Files: {', '.join(files) if files else 'n/a'}. "
        f"Tests: {args.tests}. Result: {args.result}."
    )
    tags = ["agentic", "memora", "code-change", "implementation"]
    result = register_event(
        db_path=Path(args.db_path),
        session_id=session_id,
        event_type="code_change",
        payload=payload,
        content=content,
        tags=tags,
        section=section,
        atomic_factor=atomic_factor,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_inference(args: argparse.Namespace) -> None:
    session_id = resolve_session_id(args)
    section = resolve_section(args, "inference")
    atomic_factor = resolve_atomic_factor(args, "inference")
    payload = {
        "hypothesis": args.hypothesis,
        "evidence": args.evidence,
        "uncertainty": args.uncertainty,
        "mitigation": args.mitigation,
        "section": section,
        "atomic_factor": atomic_factor,
    }
    content = (
        f"Inference [{session_id}] section={section} atomic={atomic_factor} hypothesis={args.hypothesis}. "
        f"Evidence={args.evidence}. Uncertainty={args.uncertainty}. Mitigation={args.mitigation}."
    )
    tags = ["agentic", "memora", "inference", "metacognition"]
    result = register_event(
        db_path=Path(args.db_path),
        session_id=session_id,
        event_type="inference",
        payload=payload,
        content=content,
        tags=tags,
        section=section,
        atomic_factor=atomic_factor,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_decision(args: argparse.Namespace) -> None:
    session_id = resolve_session_id(args)
    section = resolve_section(args, "decision")
    atomic_factor = resolve_atomic_factor(args, "decision")
    options = parse_csv(args.options)
    payload = {
        "question": args.question,
        "options": options,
        "selected": args.selected,
        "rationale": args.rationale,
        "effort": args.effort,
        "impact": args.impact,
        "pareto": args.pareto,
        "section": section,
        "atomic_factor": atomic_factor,
    }
    content = (
        f"Decision [{session_id}] section={section} atomic={atomic_factor} question={args.question}. "
        f"Selected={args.selected}. Rationale={args.rationale}. "
        f"Effort={args.effort}; Impact={args.impact}; Pareto={args.pareto}."
    )
    tags = ["agentic", "memora", "decision", "hitl", "pareto"]
    result = register_event(
        db_path=Path(args.db_path),
        session_id=session_id,
        event_type="decision",
        payload=payload,
        content=content,
        tags=tags,
        section=section,
        atomic_factor=atomic_factor,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_delivery(args: argparse.Namespace) -> None:
    session_id = resolve_session_id(args)
    section = resolve_section(args, "delivery")
    atomic_factor = resolve_atomic_factor(args, "delivery")
    artifacts = parse_csv(args.artifacts)
    payload = {
        "summary": args.summary,
        "artifacts": artifacts,
        "verification": args.verification,
        "section": section,
        "atomic_factor": atomic_factor,
    }
    content = (
        f"Delivery [{session_id}] section={section} atomic={atomic_factor} {args.summary}. "
        f"Artifacts: {', '.join(artifacts) if artifacts else 'n/a'}. Verification: {args.verification}."
    )
    tags = ["agentic", "memora", "delivery", "hitl"]
    result = register_event(
        db_path=Path(args.db_path),
        session_id=session_id,
        event_type="delivery",
        payload=payload,
        content=content,
        tags=tags,
        section=section,
        atomic_factor=atomic_factor,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_end(args: argparse.Namespace) -> None:
    session_id = resolve_session_id(args)
    section = resolve_section(args, "session_end")
    atomic_factor = resolve_atomic_factor(args, "session_end")
    payload = {
        "summary": args.summary,
        "next_steps": args.next_steps,
        "section": section,
        "atomic_factor": atomic_factor,
    }
    content = (
        f"Session end [{session_id}] section={section} atomic={atomic_factor} "
        f"summary={args.summary}. Next steps={args.next_steps}."
    )
    tags = ["agentic", "memora", "session-end", "hitl"]
    result = register_event(
        db_path=Path(args.db_path),
        session_id=session_id,
        event_type="session_end",
        payload=payload,
        content=content,
        tags=tags,
        section=section,
        atomic_factor=atomic_factor,
    )
    clear_active_session()
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_correlate(args: argparse.Namespace) -> None:
    db_path = Path(args.db_path)
    report_path = Path(args.report_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    ensure_parent(report_path)

    try:
        conn.execute("BEGIN IMMEDIATE")
        ensure_agentic_schema(conn)

        rows = conn.execute(
            """
            SELECT id, content, metadata, tags, created_at
            FROM memories
            WHERE json_extract(metadata, '$.event_key') IS NOT NULL
            ORDER BY id ASC
            """
        ).fetchall()

        updated = 0
        report_rows: list[dict[str, Any]] = []

        for row in rows:
            memory_id = int(row["id"])
            metadata = json.loads(row["metadata"] or "{}")
            tags = json.loads(row["tags"] or "[]")
            event_key = str(metadata.get("event_key", ""))
            event_type = str(metadata.get("event_type", "unknown"))
            session_id = str(metadata.get("session_id", "unknown"))

            reg = conn.execute(
                "SELECT payload_hash FROM agentic_event_registry WHERE event_key=?",
                (event_key,),
            ).fetchone()
            payload_hash = str(reg["payload_hash"]) if reg else hashlib.sha256(event_key.encode("utf-8")).hexdigest()

            section = sanitize_token(str(metadata.get("section") or default_section_for_event(event_type)))
            atomic_factor = sanitize_token(
                str(metadata.get("atomic_factor") or default_atomic_factor_for_event(event_type))
            )
            human_ref = str(metadata.get("human_ref") or make_human_ref(section, event_type, payload_hash))

            metadata["section"] = section
            metadata["atomic_factor"] = atomic_factor
            metadata["human_ref"] = human_ref
            tags = ensure_tags(tags if isinstance(tags, list) else [], section, atomic_factor)

            conn.execute(
                "UPDATE memories SET metadata=?, tags=? WHERE id=?",
                (
                    json.dumps(metadata, ensure_ascii=False),
                    json.dumps(tags, ensure_ascii=False),
                    memory_id,
                ),
            )

            if table_exists(conn, "memories_fts"):
                conn.execute(
                    "INSERT OR REPLACE INTO memories_fts(rowid, content, metadata, tags) VALUES (?, ?, ?, ?)",
                    (
                        memory_id,
                        row["content"],
                        json.dumps(metadata, ensure_ascii=False),
                        json.dumps(tags, ensure_ascii=False),
                    ),
                )

            upsert_section_registry(
                conn,
                human_ref=human_ref,
                event_key=event_key,
                memory_id=memory_id,
                session_id=session_id,
                event_type=event_type,
                section=section,
                atomic_factor=atomic_factor,
                payload_hash=payload_hash,
            )

            updated += 1
            report_rows.append(
                {
                    "memory_id": memory_id,
                    "human_ref": human_ref,
                    "section": section,
                    "atomic_factor": atomic_factor,
                    "event_type": event_type,
                    "session_id": session_id,
                    "created_at": row["created_at"],
                }
            )

        conn.commit()

        report_lines = [
            "# Memora Human-Readable Correlation Index",
            "",
            f"Generated at: {utc_now_str()} UTC",
            f"Updated rows: {updated}",
            "",
            "| memory_id | human_ref | section | atomic_factor | event_type | session_id | created_at |",
            "|---:|---|---|---|---|---|---|",
        ]

        for item in report_rows:
            report_lines.append(
                "| {memory_id} | `{human_ref}` | `{section}` | `{atomic_factor}` | `{event_type}` | `{session_id}` | {created_at} |".format(
                    **item
                )
            )

        report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

        print(
            json.dumps(
                {
                    "status": "correlated",
                    "updated_rows": updated,
                    "report_path": str(report_path),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    finally:
        conn.close()


def cmd_status(args: argparse.Namespace) -> None:
    db = sqlite3.connect(Path(args.db_path))
    db.row_factory = sqlite3.Row
    active = load_active_session()
    cur = db.cursor()
    ensure_agentic_schema(db)
    cur.execute("SELECT COUNT(*) AS c FROM memories")
    memories = cur.fetchone()["c"]
    cur.execute("SELECT COUNT(*) AS c FROM memories_actions")
    actions = cur.fetchone()["c"]
    cur.execute("SELECT COUNT(*) AS c FROM agentic_event_registry")
    events = cur.fetchone()["c"]
    cur.execute("SELECT COUNT(*) AS c FROM agentic_section_registry")
    sections = cur.fetchone()["c"]
    cur.execute(
        "SELECT section, COUNT(*) AS count FROM agentic_section_registry GROUP BY section ORDER BY count DESC, section ASC LIMIT 15"
    )
    section_breakdown = [dict(r) for r in cur.fetchall()]
    cur.execute(
        "SELECT event_key, session_id, event_type, memory_id, status, created_at FROM agentic_event_registry ORDER BY created_at DESC LIMIT 10"
    )
    latest = [dict(r) for r in cur.fetchall()]
    db.close()
    print(
        json.dumps(
            {
                "db_path": str(Path(args.db_path)),
                "active_session": active,
                "counts": {
                    "memories": memories,
                    "actions": actions,
                    "agentic_events": events,
                    "section_refs": sections,
                },
                "section_breakdown": section_breakdown,
                "latest_events": latest,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def add_common_event_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--section", default=None, help="Section category (human readable path).")
    parser.add_argument(
        "--atomic-factor",
        default=None,
        help="Atomic factor label used for fine-grained categorization.",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Memora workspace operations logger (atomic + idempotent)."
    )
    parser.add_argument(
        "--db-path",
        default=str(DEFAULT_DB),
        help="Path to Memora SQLite database.",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    p_start = sub.add_parser("start", help="Register session start.")
    p_start.add_argument("--session-id", default=None)
    p_start.add_argument("--agent", required=True)
    p_start.add_argument("--operator", required=True)
    p_start.add_argument("--objective", required=True)
    p_start.add_argument("--prompt-summary", required=True)
    add_common_event_args(p_start)
    p_start.set_defaults(func=cmd_start)

    p_checkpoint = sub.add_parser("checkpoint", help="Register checkpoint.")
    p_checkpoint.add_argument("--session-id", default=None)
    p_checkpoint.add_argument("--title", required=True)
    p_checkpoint.add_argument("--summary", required=True)
    p_checkpoint.add_argument("--files", default="")
    p_checkpoint.add_argument("--effort", default="medium")
    p_checkpoint.add_argument("--impact", default="medium")
    p_checkpoint.add_argument("--pareto", default="80/20")
    p_checkpoint.add_argument("--next-step", default="continue")
    add_common_event_args(p_checkpoint)
    p_checkpoint.set_defaults(func=cmd_checkpoint)

    p_change = sub.add_parser("change", help="Register code change.")
    p_change.add_argument("--session-id", default=None)
    p_change.add_argument("--summary", required=True)
    p_change.add_argument("--files", default="")
    p_change.add_argument("--tests", default="not-run")
    p_change.add_argument("--result", default="in-progress")
    add_common_event_args(p_change)
    p_change.set_defaults(func=cmd_change)

    p_inf = sub.add_parser("inference", help="Register metacognitive inference.")
    p_inf.add_argument("--session-id", default=None)
    p_inf.add_argument("--hypothesis", required=True)
    p_inf.add_argument("--evidence", required=True)
    p_inf.add_argument("--uncertainty", required=True)
    p_inf.add_argument("--mitigation", required=True)
    add_common_event_args(p_inf)
    p_inf.set_defaults(func=cmd_inference)

    p_dec = sub.add_parser("decision", help="Register decision event.")
    p_dec.add_argument("--session-id", default=None)
    p_dec.add_argument("--question", required=True)
    p_dec.add_argument("--options", required=True)
    p_dec.add_argument("--selected", required=True)
    p_dec.add_argument("--rationale", required=True)
    p_dec.add_argument("--effort", default="medium")
    p_dec.add_argument("--impact", default="medium")
    p_dec.add_argument("--pareto", default="80/20")
    add_common_event_args(p_dec)
    p_dec.set_defaults(func=cmd_decision)

    p_del = sub.add_parser("delivery", help="Register delivery/milestone.")
    p_del.add_argument("--session-id", default=None)
    p_del.add_argument("--summary", required=True)
    p_del.add_argument("--artifacts", default="")
    p_del.add_argument("--verification", default="pending")
    add_common_event_args(p_del)
    p_del.set_defaults(func=cmd_delivery)

    p_end = sub.add_parser("end", help="Register session end.")
    p_end.add_argument("--session-id", default=None)
    p_end.add_argument("--summary", required=True)
    p_end.add_argument("--next-steps", required=True)
    add_common_event_args(p_end)
    p_end.set_defaults(func=cmd_end)

    p_cor = sub.add_parser(
        "correlate",
        help="Backfill sections + atomic factors + human refs for existing agentic memories.",
    )
    p_cor.add_argument(
        "--report-path",
        default=str(DEFAULT_REPORT_PATH),
        help="Path to human-readable correlation report.",
    )
    p_cor.set_defaults(func=cmd_correlate)

    p_status = sub.add_parser("status", help="Inspect protocol and DB status.")
    p_status.set_defaults(func=cmd_status)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
