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
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB = ROOT / ".opencode" / "memory" / "memoria.db"
ACTIVE_SESSION_FILE = ROOT / ".agentic" / "active-session.json"
DEFAULT_REPORT_PATH = ROOT / ".agentic" / "memora-human-readable-index.md"
DEFAULT_VIEWS_PATH = ROOT / ".agentic" / "views.json"
RESET_CONFIRM_TOKEN = "RESET-YES"

CANONICAL_EVENT_KEYS = [
    "o_opp",
    "v_vdd",
    "i_idl",
    "q_qbr",
    "l_led",
    "k_kbi",
    "a_acc",
    "s_src",
    "e_e2e",
    "b_b2b",
    "n_n2c",
    "h_hor",
    "t_tzo",
    "d_dat",
]

CANONICAL_IAM_KEYS = [
    "u_usr",
    "w_www",
    "m_mob",
    "c_con",
    "x_pwd",
    "f_hom",
    "z_zon",
]

CANONICAL_PATTERNS: dict[str, str] = {
    "o_opp": r"^o_[a-z0-9-]+$",
    "v_vdd": r"^v_[a-z0-9-]+$",
    "i_idl": r"^i_q-l-k-a-s-e-b-n-h-t-d$",
    "k_kbi": r"^k_\d{8}-\d{6}$",
    "h_hor": r"^h_\d{2}-\d{2}-\d{2}$",
    "t_tzo": r"^t_\d+-[A-Za-z_]+/[A-Za-z_]+$",
    "d_dat": r"^d_\d{2}-\d{2}-\d{2}$",
    "u_usr": r"^u_\d+-\$\{a_\*-\}-[A-Za-z0-9_-]+$",
    "w_www": r"^w_[a-z0-9-]+$",
    "m_mob": r"^m_\d{8,16}$",
    "f_hom": r"^f_home-\$\{u_\d+}$",
    "z_zon": r"^z_\d+-c_\d+-u_\d+$",
}

ROLE_CATALOG: dict[int, str] = {
    1: "admin-is-user",
    2: "super-is-guest",
    44: "supermario-is-sudo",
    51: "luigi-is-admin",
    63: "yoshi-is-manager",
    86: "isBrito",
}

ZONE_CATALOG: dict[int, str] = {
    254: "godBrito",
    1986: "sudoRoot",
    1999: "neo",
    2000: "y2k",
    2500: "staff",
    2666: "powerUser",
    2699: "editor",
    2700: "collaborator",
    2800: "audit",
    3000: "userManager",
    4000: "communityModerator",
    4500: "teamsModerator",
    5000: "editWriteRead",
    9900: "selfData",
    9950: "readContent",
    9980: "canLogin",
    9984: "resetPasswd",
    9985: "ssoOauth",
    9995: "canSignIn",
    9997: "viewPage",
    9998: "redirectHome",
    9999: "limitedView",
}

CANONICAL_CLUSTERS = {
    "project.master",
    "session.master",
    "session.start",
    "session.resume",
    "session.hidden",
    "ws.features",
    "ws.plan",
    "ws.error_bug_fix",
    "ws.research_improve",
    "ws.build_plan_fix",
    "project.commit_merge",
    "project.sync_status",
}

LEXICAL_ALIASES: dict[str, str] = {
    "init": "session.start",
    "start": "session.start",
    "new": "session.start",
    "resume": "session.resume",
    "continue": "session.resume",
    "discard": "session.hidden",
    "hide": "session.hidden",
    "roadmap": "ws.features",
    "features": "ws.features",
    "plan": "ws.plan",
    "backlog": "ws.plan",
    "issue": "ws.error_bug_fix",
    "issues": "ws.error_bug_fix",
    "fix": "ws.error_bug_fix",
    "error": "ws.error_bug_fix",
    "errors": "ws.error_bug_fix",
    "bug": "ws.error_bug_fix",
    "research": "ws.research_improve",
    "enhance": "ws.research_improve",
    "improve": "ws.research_improve",
    "build": "ws.build_plan_fix",
    "commit/merge": "project.commit_merge",
    "sync/status": "project.sync_status",
}

EDGE_MATRIX = [
    {"id": "E001", "from": "project.master", "to": "session.master", "type": "contains", "score": 1.00},
    {"id": "E002", "from": "session.start", "to": "session.resume", "type": "enables", "score": 0.90},
    {"id": "E003", "from": "session.resume", "to": "ws.plan", "type": "enables", "score": 0.86},
    {"id": "E004", "from": "ws.plan", "to": "ws.features", "type": "enables", "score": 0.92},
    {"id": "E005", "from": "ws.build_plan_fix", "to": "ws.features", "type": "implements", "score": 0.95},
    {"id": "E006", "from": "ws.error_bug_fix", "to": "ws.plan", "type": "refines", "score": 0.88},
    {"id": "E007", "from": "ws.error_bug_fix", "to": "ws.build_plan_fix", "type": "validates", "score": 0.90},
    {"id": "E008", "from": "ws.research_improve", "to": "ws.plan", "type": "refines", "score": 0.84},
    {"id": "E009", "from": "project.commit_merge", "to": "project.sync_status", "type": "validates", "score": 0.91},
    {"id": "E010", "from": "session.hidden", "to": "session.master", "type": "state_change", "score": 1.00},
]

DUPLICATE_ALLOWED_EDGE_TYPES = {"related_to", "near_duplicate"}
DUPLICATE_ALLOWED_SOURCES = {"embedding_auto", "semantic_similarity"}
DEFAULT_CAUSAL_MERGE_WINDOW_HOURS = 4

CAUSAL_TOP_ORDER = {"0": 0, "1": 1, "5": 2, "9": 3}


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
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS agentic_canonical_registry (
            idempotency_key TEXT PRIMARY KEY,
            payload_hash TEXT NOT NULL,
            project_master_key TEXT NOT NULL,
            session_master_key TEXT NOT NULL,
            session_id TEXT NOT NULL,
            o_opp TEXT NOT NULL,
            v_vdd TEXT NOT NULL,
            schema_version TEXT NOT NULL DEFAULT 'canonical-normalized.v1',
            memory_root_id INTEGER,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS agentic_atomic_registry (
            segment_key TEXT PRIMARY KEY,
            idempotency_key TEXT NOT NULL,
            segment_name TEXT NOT NULL,
            cluster_primary TEXT NOT NULL,
            clusters_secondary TEXT,
            memory_id INTEGER,
            section TEXT NOT NULL,
            atomic_factor TEXT NOT NULL,
            visibility TEXT NOT NULL DEFAULT 'active',
            session_id TEXT NOT NULL,
            payload_hash TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS agentic_cluster_edges (
            edge_key TEXT PRIMARY KEY,
            idempotency_key TEXT NOT NULL,
            from_memory_id INTEGER NOT NULL,
            to_memory_id INTEGER NOT NULL,
            edge_type TEXT NOT NULL,
            source TEXT NOT NULL,
            score REAL NOT NULL,
            duplicate_eligible INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT
        )
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_agentic_atomic_session ON agentic_atomic_registry(session_id)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_agentic_atomic_memory ON agentic_atomic_registry(memory_id)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_agentic_cluster_edges_from_to ON agentic_cluster_edges(from_memory_id, to_memory_id)"
    )


def sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalize_cluster_token(value: str | None) -> str:
    raw = str(value or "").strip().lower()
    if not raw:
        return "ws.plan"
    if raw.startswith("cluster:"):
        raw = raw.split(":", 1)[1]
    raw = re.sub(r"[^a-z0-9._/-]+", "", raw)

    for candidate in [
        raw,
        raw.replace("-", "_"),
        raw.replace("/", "_"),
        raw.replace("-", "."),
        raw.replace("_", "."),
    ]:
        if candidate in CANONICAL_CLUSTERS:
            return candidate

    alias_candidate = (
        LEXICAL_ALIASES.get(raw)
        or LEXICAL_ALIASES.get(raw.replace("-", "_"))
        or LEXICAL_ALIASES.get(raw.replace("_", "/"))
    )
    if alias_candidate and alias_candidate in CANONICAL_CLUSTERS:
        return alias_candidate
    return "ws.plan"


def canonical_line_match(line: str) -> tuple[str, str] | None:
    match = re.match(r"^\s*\[([a-z]_[a-z0-9]+)\]\s*:\s*(.*?)\s*(?:#.*)?$", line, flags=re.I)
    if not match:
        return None
    return match.group(1), match.group(2)


def parse_canonical_dsl(raw: str) -> dict[str, str]:
    data: dict[str, str] = {}
    for idx, line in enumerate(raw.splitlines(), start=1):
        tline = line.strip()
        if not tline or tline.startswith("#") or tline.startswith("---"):
            continue
        parsed = canonical_line_match(line)
        if not parsed:
            raise SystemExit(f"E_PARSE_SYNTAX at line {idx}: {line}")
        key, value = parsed
        if key in data:
            raise SystemExit(f"E_PARSE_DUPLICATE key={key} line={idx}")
        data[key] = value
    return data


def validate_canonical_record(record: dict[str, str]) -> None:
    missing_event = [k for k in CANONICAL_EVENT_KEYS if k not in record]
    missing_iam = [k for k in CANONICAL_IAM_KEYS if k not in record]
    if missing_event:
        raise SystemExit(f"E_PARSE_MISSING_EVENT keys={missing_event}")
    if missing_iam:
        raise SystemExit(f"E_PARSE_MISSING_IAM keys={missing_iam}")

    for key, pattern in CANONICAL_PATTERNS.items():
        value = record.get(key, "")
        if not re.match(pattern, value):
            raise SystemExit(f"E_PARSE_FORMAT key={key} value={value} pattern={pattern}")

    role_match = re.match(r"^c_(\d+)-", record["c_con"])
    if not role_match:
        raise SystemExit("E_IAM_FORMAT key=c_con expected c_<num>-...")
    role_code = int(role_match.group(1))
    if role_code not in ROLE_CATALOG:
        raise SystemExit(f"E_IAM_ROLE unsupported role code={role_code}")

    zone_match = re.match(r"^z_(\d+)-c_(\d+)-u_(\d+)$", record["z_zon"])
    if not zone_match:
        raise SystemExit("E_IAM_FORMAT key=z_zon expected z_<level>-c_<code>-u_<code>")
    zone_level = int(zone_match.group(1))
    zone_role_code = int(zone_match.group(2))
    if zone_level not in ZONE_CATALOG:
        raise SystemExit(f"E_IAM_ZONE unsupported zone level={zone_level}")
    if role_code != zone_role_code:
        raise SystemExit(f"E_IAM_INCONSISTENCY c_con={role_code} z_zon.c={zone_role_code}")


def normalize_canonical_record(record: dict[str, str]) -> dict[str, Any]:
    validate_canonical_record(record)
    normalized = {
        "schema_version": "canonical-normalized.v1",
        "event_layer": {k: record[k] for k in CANONICAL_EVENT_KEYS},
        "iam_layer": {k: record[k] for k in CANONICAL_IAM_KEYS},
    }
    payload_hash = sha256_hex(canonical_json(normalized))
    idempotency_key = sha256_hex(f"{payload_hash}:canonical-normalized.v1")
    normalized["metadata"] = {
        "payload_hash": payload_hash,
        "idempotency_key": idempotency_key,
        "normalized_at_utc": utc_now_str(),
    }
    return normalized


def parse_crossrefs_blob(raw: str | None) -> list[dict[str, Any]]:
    if not raw:
        return []
    try:
        data = json.loads(raw)
    except Exception:
        return []
    if not isinstance(data, list):
        return []
    return [x for x in data if isinstance(x, dict)]


def get_crossrefs(conn: sqlite3.Connection, memory_id: int) -> list[dict[str, Any]]:
    if not table_exists(conn, "memories_crossrefs"):
        return []
    row = conn.execute(
        "SELECT related FROM memories_crossrefs WHERE memory_id=?",
        (memory_id,),
    ).fetchone()
    return parse_crossrefs_blob(row[0] if row else None)


def upsert_crossrefs(conn: sqlite3.Connection, memory_id: int, refs: list[dict[str, Any]]) -> None:
    payload = json.dumps(
        sorted(refs, key=lambda x: (int(x.get("id", -1)), str(x.get("edge_type", "")), str(x.get("source", "")))),
        ensure_ascii=False,
    )
    conn.execute(
        """
        INSERT INTO memories_crossrefs(memory_id, related)
        VALUES (?, ?)
        ON CONFLICT(memory_id) DO UPDATE SET related=excluded.related
        """,
        (memory_id, payload),
    )


def upsert_directed_edge(
    conn: sqlite3.Connection,
    *,
    idempotency_key: str,
    from_memory_id: int,
    to_memory_id: int,
    edge_type: str,
    score: float,
    source: str,
    duplicate_eligible: bool,
) -> None:
    refs = get_crossrefs(conn, from_memory_id)
    kept = [r for r in refs if int(r.get("id", -1)) != to_memory_id]
    kept.append(
        {
            "id": to_memory_id,
            "score": score,
            "edge_type": edge_type,
            "source": source,
            "duplicate_eligible": bool(duplicate_eligible),
        }
    )
    upsert_crossrefs(conn, from_memory_id, kept)

    edge_key = sha256_hex(
        f"{idempotency_key}:{from_memory_id}:{to_memory_id}:{edge_type}:{source}"
    )
    conn.execute(
        """
        INSERT INTO agentic_cluster_edges(
            edge_key, idempotency_key, from_memory_id, to_memory_id, edge_type, source, score, duplicate_eligible, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(edge_key) DO UPDATE SET
            score=excluded.score,
            duplicate_eligible=excluded.duplicate_eligible,
            updated_at=excluded.updated_at
        """,
        (
            edge_key,
            idempotency_key,
            from_memory_id,
            to_memory_id,
            edge_type,
            source,
            score,
            1 if duplicate_eligible else 0,
            utc_now_str(),
        ),
    )


def update_memory_record(
    conn: sqlite3.Connection,
    *,
    memory_id: int,
    content: str,
    metadata: dict[str, Any],
    tags: list[str],
) -> None:
    metadata_json = json.dumps(metadata, ensure_ascii=False)
    tags_json = json.dumps(tags, ensure_ascii=False)
    conn.execute(
        "UPDATE memories SET content=?, metadata=?, tags=?, updated_at=? WHERE id=?",
        (content, metadata_json, tags_json, utc_now_str(), memory_id),
    )
    if table_exists(conn, "memories_fts"):
        conn.execute(
            "INSERT OR REPLACE INTO memories_fts(rowid, content, metadata, tags) VALUES (?, ?, ?, ?)",
            (memory_id, content, metadata_json, tags_json),
        )


def ensure_unique_list(items: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for item in items:
        if item and item not in seen:
            out.append(item)
            seen.add(item)
    return out


def normalize_duplicate_policy(conn: sqlite3.Connection) -> dict[str, int]:
    if not table_exists(conn, "memories_crossrefs"):
        return {"rows_updated": 0, "edges_adjusted": 0}
    rows = conn.execute("SELECT memory_id, related FROM memories_crossrefs").fetchall()
    rows_updated = 0
    edges_adjusted = 0
    for row in rows:
        memory_id = int(row[0])
        refs = parse_crossrefs_blob(row[1])
        changed = False
        for ref in refs:
            score = float(ref.get("score", 0.0))
            edge_type = str(ref.get("edge_type", "")).strip().lower()
            source = str(ref.get("source", "")).strip().lower()
            ref["edge_type"] = edge_type
            ref["source"] = source
            allowed = (
                edge_type in DUPLICATE_ALLOWED_EDGE_TYPES
                or source in DUPLICATE_ALLOWED_SOURCES
            )
            if score >= 0.85 and not allowed:
                ref["score"] = 0.84
                ref["duplicate_eligible"] = False
                changed = True
                edges_adjusted += 1
        if changed:
            upsert_crossrefs(conn, memory_id, refs)
            rows_updated += 1
    return {"rows_updated": rows_updated, "edges_adjusted": edges_adjusted}


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
    section_tag = f"section:{sanitize_token(section)}"
    atomic_tag = f"atomic:{sanitize_token(atomic_factor)}"
    merged = [section_tag, atomic_tag, *tags]

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


def reset_table(conn: sqlite3.Connection, table: str) -> int:
    if not table_exists(conn, table):
        return 0
    row = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
    count = int(row[0]) if row else 0
    conn.execute(f"DELETE FROM {table}")
    return count


def cmd_reset_hard(args: argparse.Namespace) -> None:
    if args.confirm != RESET_CONFIRM_TOKEN:
        raise SystemExit(
            f"Reset blocked. Pass --confirm {RESET_CONFIRM_TOKEN} to execute destructive reset."
        )

    db_path = Path(args.db_path)
    ensure_parent(db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    reset_counts: dict[str, int] = {}
    try:
        conn.execute("BEGIN IMMEDIATE")
        ensure_agentic_schema(conn)

        tables = [
            "agentic_cluster_edges",
            "agentic_atomic_registry",
            "agentic_canonical_registry",
            "agentic_section_registry",
            "agentic_event_registry",
            "memories_actions",
            "memories_events",
            "memories_embeddings",
            "memories_crossrefs",
            "memories",
            "memories_meta",
        ]
        for table in tables:
            reset_counts[table] = reset_table(conn, table)

        if table_exists(conn, "memories_fts"):
            conn.execute("INSERT INTO memories_fts(memories_fts) VALUES('delete-all')")

        seq_names = ",".join(
            [f"'{name}'" for name in ["memories", "memories_actions", "memories_events"]]
        )
        if table_exists(conn, "sqlite_sequence"):
            conn.execute(f"DELETE FROM sqlite_sequence WHERE name IN ({seq_names})")

        conn.commit()
    finally:
        conn.close()

    clear_active_session()
    views_removed = False
    if DEFAULT_VIEWS_PATH.exists():
        DEFAULT_VIEWS_PATH.unlink()
        views_removed = True

    print(
        json.dumps(
            {
                "status": "reset_complete",
                "db_path": str(db_path),
                "reset_counts": reset_counts,
                "views_removed": views_removed,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def resolve_canonical_session_id(args: argparse.Namespace) -> str:
    if args.session_id:
        return args.session_id
    active = load_active_session()
    if active and active.get("session_id"):
        return str(active["session_id"])
    return make_session_id("canonical")


def build_segment_blueprint(session_state: str) -> list[dict[str, Any]]:
    state_map = {
        "start": "session.start",
        "resume": "session.resume",
        "hidden": "session.hidden",
    }
    lifecycle_cluster = state_map.get(session_state, "session.start")
    lifecycle_visibility = "hidden" if lifecycle_cluster == "session.hidden" else "active"

    return [
        {
            "segment_name": "project.master",
            "cluster_primary": "project.master",
            "clusters_secondary": ["session.master", "project.commit_merge", "project.sync_status"],
            "section": "governance/project",
            "atomic_factor": "project-master",
            "visibility": "active",
        },
        {
            "segment_name": "session.master",
            "cluster_primary": "session.master",
            "clusters_secondary": ["ws.plan", lifecycle_cluster],
            "section": "governance/session",
            "atomic_factor": "session-master",
            "visibility": "active",
        },
        {
            "segment_name": lifecycle_cluster,
            "cluster_primary": lifecycle_cluster,
            "clusters_secondary": ["session.master", "ws.plan"],
            "section": "governance/session",
            "atomic_factor": "session-lifecycle",
            "visibility": lifecycle_visibility,
        },
        {
            "segment_name": "ws.plan",
            "cluster_primary": "ws.plan",
            "clusters_secondary": ["ws.features", "ws.error_bug_fix", "ws.research_improve"],
            "section": "delivery/plan",
            "atomic_factor": "planning-atomicity",
            "visibility": "active",
        },
        {
            "segment_name": "ws.features",
            "cluster_primary": "ws.features",
            "clusters_secondary": ["ws.plan", "ws.build_plan_fix"],
            "section": "delivery/features",
            "atomic_factor": "feature-correlation",
            "visibility": "active",
        },
        {
            "segment_name": "ws.error_bug_fix",
            "cluster_primary": "ws.error_bug_fix",
            "clusters_secondary": ["ws.plan", "ws.build_plan_fix"],
            "section": "analysis/errors",
            "atomic_factor": "error-resolution",
            "visibility": "active",
        },
        {
            "segment_name": "ws.research_improve",
            "cluster_primary": "ws.research_improve",
            "clusters_secondary": ["ws.plan"],
            "section": "analysis/research",
            "atomic_factor": "research-improvement",
            "visibility": "active",
        },
        {
            "segment_name": "ws.build_plan_fix",
            "cluster_primary": "ws.build_plan_fix",
            "clusters_secondary": ["ws.features"],
            "section": "implementation/build",
            "atomic_factor": "build-fix-implementation",
            "visibility": "active",
        },
        {
            "segment_name": "project.commit_merge",
            "cluster_primary": "project.commit_merge",
            "clusters_secondary": ["project.sync_status", "project.master"],
            "section": "delivery/release",
            "atomic_factor": "commit-merge-flow",
            "visibility": "active",
        },
        {
            "segment_name": "project.sync_status",
            "cluster_primary": "project.sync_status",
            "clusters_secondary": ["project.master"],
            "section": "delivery/status",
            "atomic_factor": "sync-status-flow",
            "visibility": "active",
        },
    ]


def register_segment_event(
    conn: sqlite3.Connection,
    *,
    event_key: str,
    session_id: str,
    payload_hash: str,
    memory_id: int,
    event_type: str,
    section: str,
    atomic_factor: str,
) -> None:
    human_ref = f"{make_human_ref(section, event_type, payload_hash)}-{sha256_hex(event_key)[:6]}"
    conn.execute(
        """
        INSERT INTO agentic_event_registry(event_key, session_id, event_type, payload_hash, memory_id, status, updated_at)
        VALUES (?, ?, ?, ?, ?, 'applied', ?)
        ON CONFLICT(event_key) DO UPDATE SET
            session_id=excluded.session_id,
            event_type=excluded.event_type,
            payload_hash=excluded.payload_hash,
            memory_id=excluded.memory_id,
            status='applied',
            updated_at=excluded.updated_at
        """,
        (event_key, session_id, event_type, payload_hash, memory_id, utc_now_str()),
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


def cmd_canonical_ingest(args: argparse.Namespace) -> None:
    dsl_path = Path(args.dsl)
    if not dsl_path.exists():
        raise SystemExit(f"DSL file not found: {dsl_path}")

    session_id = resolve_canonical_session_id(args)
    raw = dsl_path.read_text(encoding="utf-8")
    record = parse_canonical_dsl(raw)
    normalized = normalize_canonical_record(record)
    payload_hash = normalized["metadata"]["payload_hash"]
    idempotency_key = normalized["metadata"]["idempotency_key"]
    project_master_key = sha256_hex(
        f"{record['o_opp']}:{record['v_vdd']}:{normalized['schema_version']}"
    )
    session_master_key = sha256_hex(f"{project_master_key}:{session_id}")

    conn = sqlite3.connect(Path(args.db_path))
    conn.row_factory = sqlite3.Row

    created_segments = 0
    updated_segments = 0
    memory_by_cluster: dict[str, int] = {}

    try:
        conn.execute("BEGIN IMMEDIATE")
        ensure_agentic_schema(conn)

        conn.execute(
            """
            INSERT INTO agentic_canonical_registry(
                idempotency_key, payload_hash, project_master_key, session_master_key, session_id, o_opp, v_vdd, schema_version, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(idempotency_key) DO UPDATE SET
                payload_hash=excluded.payload_hash,
                project_master_key=excluded.project_master_key,
                session_master_key=excluded.session_master_key,
                session_id=excluded.session_id,
                o_opp=excluded.o_opp,
                v_vdd=excluded.v_vdd,
                schema_version=excluded.schema_version,
                updated_at=excluded.updated_at
            """,
            (
                idempotency_key,
                payload_hash,
                project_master_key,
                session_master_key,
                session_id,
                record["o_opp"],
                record["v_vdd"],
                normalized["schema_version"],
                utc_now_str(),
            ),
        )

        for segment in build_segment_blueprint(args.session_state):
            segment_name = segment["segment_name"]
            segment_key = sha256_hex(f"{idempotency_key}:{segment_name}")
            event_type = "canonical_segment"
            event_key = f"{event_type}:{session_id}:{segment_key[:24]}"
            section = segment["section"]
            atomic_factor = segment["atomic_factor"]
            cluster_primary = normalize_cluster_token(segment["cluster_primary"])
            secondary = [
                normalize_cluster_token(item) for item in segment.get("clusters_secondary", [])
            ]
            secondary = [item for item in secondary if item != cluster_primary]
            visibility = "hidden" if segment.get("visibility") == "hidden" else "active"

            metadata = {
                "schema_version": normalized["schema_version"],
                "event_key": event_key,
                "event_type": event_type,
                "session_id": session_id,
                "section": sanitize_token(section),
                "atomic_factor": sanitize_token(atomic_factor),
                "cluster_primary": cluster_primary,
                "cluster_secondary": secondary,
                "visibility": visibility,
                "canonical": {
                    "o_opp": record["o_opp"],
                    "v_vdd": record["v_vdd"],
                    "payload_hash": payload_hash,
                    "idempotency_key": idempotency_key,
                    "project_master_key": project_master_key,
                    "session_master_key": session_master_key,
                    "segment_key": segment_key,
                },
            }

            content = (
                f"Canonical segment [{segment_name}] session={session_id} "
                f"o_opp={record['o_opp']} v_vdd={record['v_vdd']} "
                f"cluster_primary={cluster_primary} visibility={visibility}."
            )
            tags = ensure_unique_list(
                ensure_tags(
                    [
                        "canonical",
                        "ssot-v1",
                        f"cluster:{cluster_primary}",
                        f"session:{session_id}",
                        *[f"cluster:{item}" for item in secondary],
                    ],
                    section,
                    atomic_factor,
                )
            )

            existing_row = conn.execute(
                "SELECT memory_id FROM agentic_atomic_registry WHERE segment_key=?",
                (segment_key,),
            ).fetchone()
            memory_id: int
            if existing_row and existing_row["memory_id"]:
                memory_id = int(existing_row["memory_id"])
                update_memory_record(
                    conn,
                    memory_id=memory_id,
                    content=content,
                    metadata=metadata,
                    tags=tags,
                )
                updated_segments += 1
            else:
                memory_id = insert_memory_record(
                    conn,
                    content=content,
                    metadata=metadata,
                    tags=tags,
                    event_type=event_type,
                    event_key=event_key,
                )
                created_segments += 1

            register_segment_event(
                conn,
                event_key=event_key,
                session_id=session_id,
                payload_hash=payload_hash,
                memory_id=memory_id,
                event_type=event_type,
                section=sanitize_token(section),
                atomic_factor=sanitize_token(atomic_factor),
            )

            conn.execute(
                """
                INSERT INTO agentic_atomic_registry(
                    segment_key, idempotency_key, segment_name, cluster_primary, clusters_secondary,
                    memory_id, section, atomic_factor, visibility, session_id, payload_hash, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(segment_key) DO UPDATE SET
                    idempotency_key=excluded.idempotency_key,
                    segment_name=excluded.segment_name,
                    cluster_primary=excluded.cluster_primary,
                    clusters_secondary=excluded.clusters_secondary,
                    memory_id=excluded.memory_id,
                    section=excluded.section,
                    atomic_factor=excluded.atomic_factor,
                    visibility=excluded.visibility,
                    session_id=excluded.session_id,
                    payload_hash=excluded.payload_hash,
                    updated_at=excluded.updated_at
                """,
                (
                    segment_key,
                    idempotency_key,
                    segment_name,
                    cluster_primary,
                    json.dumps(secondary, ensure_ascii=False),
                    memory_id,
                    sanitize_token(section),
                    sanitize_token(atomic_factor),
                    visibility,
                    session_id,
                    payload_hash,
                    utc_now_str(),
                ),
            )

            memory_by_cluster[cluster_primary] = memory_id

        for edge in EDGE_MATRIX:
            src_cluster = normalize_cluster_token(edge["from"])
            dst_cluster = normalize_cluster_token(edge["to"])
            from_id = memory_by_cluster.get(src_cluster)
            to_id = memory_by_cluster.get(dst_cluster)
            if not from_id or not to_id:
                continue
            upsert_directed_edge(
                conn,
                idempotency_key=idempotency_key,
                from_memory_id=from_id,
                to_memory_id=to_id,
                edge_type=str(edge["type"]),
                score=float(edge["score"]),
                source="ssot_edge_matrix_v1",
                duplicate_eligible=False,
            )

        root_memory = memory_by_cluster.get("project.master")
        conn.execute(
            """
            UPDATE agentic_canonical_registry
            SET memory_root_id=?, updated_at=?
            WHERE idempotency_key=?
            """,
            (root_memory, utc_now_str(), idempotency_key),
        )
        conn.commit()
    finally:
        conn.close()

    print(
        json.dumps(
            {
                "status": "canonical_ingested",
                "session_id": session_id,
                "payload_hash": payload_hash,
                "idempotency_key": idempotency_key,
                "project_master_key": project_master_key,
                "session_master_key": session_master_key,
                "created_segments": created_segments,
                "updated_segments": updated_segments,
                "clusters": sorted(memory_by_cluster.keys()),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def infer_clusters_from_memory(memory: sqlite3.Row) -> tuple[str, list[str], str]:
    metadata: dict[str, Any] = {}
    tags: list[str] = []
    try:
        metadata = json.loads(memory["metadata"] or "{}")
    except Exception:
        metadata = {}
    try:
        tags = json.loads(memory["tags"] or "[]")
    except Exception:
        tags = []

    primary = normalize_cluster_token(str(metadata.get("cluster_primary") or ""))
    secondaries = metadata.get("cluster_secondary") or []
    if not isinstance(secondaries, list):
        secondaries = []
    normalized_secondaries = [normalize_cluster_token(str(item)) for item in secondaries]

    if not memory["metadata"] or not metadata.get("cluster_primary"):
        candidates: list[str] = []
        content = str(memory["content"] or "").lower()
        for raw, canonical in LEXICAL_ALIASES.items():
            if raw in content:
                candidates.append(canonical)
        for tag in tags:
            raw = str(tag).lower()
            raw = raw.split(":", 1)[-1] if raw.startswith("cluster:") else raw
            raw = raw.replace("-", "_")
            mapped = LEXICAL_ALIASES.get(raw) or LEXICAL_ALIASES.get(raw.replace("_", "/"))
            if mapped:
                candidates.append(mapped)
        if candidates:
            primary = candidates[0]
            normalized_secondaries.extend(candidates[1:])

    visibility = str(metadata.get("visibility") or "active")
    if primary == "session.hidden":
        visibility = "hidden"
    if visibility not in {"active", "hidden"}:
        visibility = "active"

    normalized_secondaries = ensure_unique_list(
        [item for item in normalized_secondaries if item != primary]
    )
    return primary, normalized_secondaries, visibility


def parse_memory_dt(ts: str | None) -> datetime | None:
    if not ts:
        return None
    raw = str(ts).split(".", 1)[0]
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    return None


def extract_section(metadata: dict[str, Any]) -> str:
    hierarchy = metadata.get("hierarchy", {})
    if isinstance(hierarchy, dict):
        path = hierarchy.get("path")
        if isinstance(path, list) and path:
            head = str(path[0]).strip("/")
            tail = "/".join(str(x).strip("/") for x in path[1:] if str(x).strip("/"))
            return f"{head}/{tail}".strip("/") if tail else head
    section = str(metadata.get("section") or "").strip("/")
    subsection = str(metadata.get("subsection") or "").strip("/")
    if section and subsection:
        return f"{section}/{subsection}".strip("/")
    if section:
        return section
    return "uncategorized"


def causal_path_for_metadata(metadata: dict[str, Any], session_bucket: str) -> list[str]:
    section = extract_section(metadata).lower()
    cluster_primary = str(metadata.get("cluster_primary") or "").lower()

    if cluster_primary.startswith("session.") or section.startswith("session/") or section == "session":
        return ["0", f"0.{sanitize_token(session_bucket).replace('/', '-')}"]
    if section.startswith("implementation/"):
        sub = sanitize_token(section.split("/", 1)[1]).replace("/", "-")
        return ["1", f"1.{sub}"]
    if section == "delivery/pilot":
        return ["1", "1.2", "1.2.pilot"]
    if section in {"delivery/features", "delivery/graph"}:
        sub = sanitize_token(section.split("/", 1)[1]).replace("/", "-")
        return ["1", "1.4", f"1.4.{sub}"]
    if section == "delivery/release":
        return ["5", "5.1"]
    if section == "delivery/closure":
        return ["5", "5.2"]
    if section == "delivery/status":
        return ["5", "5.3"]
    if section.startswith("analysis/"):
        sub = sanitize_token(section.split("/", 1)[1]).replace("/", "-")
        return ["9", "9.1", f"9.1.{sub}"]
    if section.startswith("governance/") or section == "governance":
        sub = sanitize_token(section.split("/", 1)[1] if "/" in section else "general").replace("/", "-")
        return ["9", "9.2", f"9.2.{sub}"]
    if section.startswith("memory"):
        return ["9", "9.3"]
    if section.startswith("platform"):
        return ["9", "9.4"]
    if section.startswith("operations"):
        return ["9", "9.0"]
    return ["9", "9.9"]


def build_session_bucket_map(rows: list[sqlite3.Row], merge_window_hours: int) -> tuple[dict[int, str], list[dict[str, Any]]]:
    sessions: dict[str, dict[str, Any]] = {}
    for row in rows:
        metadata = json.loads(row["metadata"] or "{}")
        session_id = str(
            metadata.get("session_id")
            or metadata.get("session")
            or metadata.get("sessionId")
            or "unknown-session"
        )
        ts = parse_memory_dt(row["updated_at"] or row["created_at"])
        entry = sessions.setdefault(
            session_id,
            {"session_id": session_id, "start": None, "end": None, "memory_ids": []},
        )
        entry["memory_ids"].append(int(row["id"]))
        if ts:
            entry["start"] = ts if entry["start"] is None or ts < entry["start"] else entry["start"]
            entry["end"] = ts if entry["end"] is None or ts > entry["end"] else entry["end"]

    ordered = sorted(
        sessions.values(),
        key=lambda item: (item["start"] is None, item["start"] or datetime.min, item["session_id"]),
    )
    window = timedelta(hours=max(1, int(merge_window_hours)))
    buckets: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    used: set[str] = set()

    def create_bucket(item: dict[str, Any]) -> dict[str, Any]:
        base = item["start"].strftime("%Y%m%d-%H%M") if item["start"] else f"unknown-{sanitize_token(item['session_id'])[:8]}"
        bucket_id = base
        idx = 1
        while bucket_id in used:
            idx += 1
            bucket_id = f"{base}-{idx}"
        used.add(bucket_id)
        return {
            "bucket_id": bucket_id,
            "start": item["start"],
            "end": item["end"],
            "session_ids": [item["session_id"]],
            "memory_ids": list(item["memory_ids"]),
        }

    for item in ordered:
        if current is None:
            current = create_bucket(item)
            buckets.append(current)
            continue
        can_merge = (
            item["start"] is not None
            and current["end"] is not None
            and item["start"] - current["end"] <= window
        )
        if can_merge:
            current["session_ids"].append(item["session_id"])
            current["memory_ids"].extend(item["memory_ids"])
            if item["end"] and (current["end"] is None or item["end"] > current["end"]):
                current["end"] = item["end"]
            if item["start"] and (current["start"] is None or item["start"] < current["start"]):
                current["start"] = item["start"]
        else:
            current = create_bucket(item)
            buckets.append(current)

    memory_to_bucket: dict[int, str] = {}
    for bucket in buckets:
        unique_ids = sorted(set(int(x) for x in bucket["memory_ids"]))
        bucket["memory_ids"] = unique_ids
        for mid in unique_ids:
            memory_to_bucket[mid] = bucket["bucket_id"]

    return memory_to_bucket, buckets


def cmd_recompute_clusters(args: argparse.Namespace) -> None:
    if args.mode != "session-master":
        raise SystemExit("Unsupported mode. Use --mode session-master")

    conn = sqlite3.connect(Path(args.db_path))
    conn.row_factory = sqlite3.Row
    updated = 0
    edge_upserts = 0
    duplicate_normalization = {"rows_updated": 0, "edges_adjusted": 0}

    try:
        conn.execute("BEGIN IMMEDIATE")
        ensure_agentic_schema(conn)
        rows = conn.execute(
            "SELECT id, content, metadata, tags FROM memories ORDER BY id ASC"
        ).fetchall()

        latest_by_session_cluster: dict[str, dict[str, int]] = {}

        for row in rows:
            memory_id = int(row["id"])
            primary, secondaries, visibility = infer_clusters_from_memory(row)

            metadata = json.loads(row["metadata"] or "{}")
            tags = json.loads(row["tags"] or "[]")
            session_id = str(
                metadata.get("session_id")
                or metadata.get("session")
                or metadata.get("sessionId")
                or "unknown-session"
            )

            metadata["cluster_primary"] = primary
            metadata["cluster_secondary"] = secondaries
            metadata["visibility"] = visibility
            metadata["session_id"] = session_id

            tags = ensure_unique_list(
                ensure_tags(
                    [*tags, f"cluster:{primary}", *[f"cluster:{item}" for item in secondaries]],
                    str(metadata.get("section") or "delivery/plan"),
                    str(metadata.get("atomic_factor") or "cluster-recompute"),
                )
            )
            update_memory_record(
                conn,
                memory_id=memory_id,
                content=row["content"],
                metadata=metadata,
                tags=tags,
            )
            updated += 1

            if visibility == "active":
                latest_by_session_cluster.setdefault(session_id, {})[primary] = memory_id

        for session_id, cluster_map in latest_by_session_cluster.items():
            synthetic_idempotency = sha256_hex(f"recompute:{session_id}:session-master")
            for edge in EDGE_MATRIX:
                src = normalize_cluster_token(edge["from"])
                dst = normalize_cluster_token(edge["to"])
                from_id = cluster_map.get(src)
                to_id = cluster_map.get(dst)
                if not from_id or not to_id:
                    continue
                upsert_directed_edge(
                    conn,
                    idempotency_key=synthetic_idempotency,
                    from_memory_id=from_id,
                    to_memory_id=to_id,
                    edge_type=str(edge["type"]),
                    score=float(edge["score"]),
                    source="ssot_edge_matrix_v1",
                    duplicate_eligible=False,
                )
                edge_upserts += 1

        duplicate_normalization = normalize_duplicate_policy(conn)
        conn.commit()
    finally:
        conn.close()

    print(
        json.dumps(
            {
                "status": "recomputed",
                "mode": args.mode,
                "memories_updated": updated,
                "edge_upserts": edge_upserts,
                "duplicate_normalization": duplicate_normalization,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def cmd_recompute_causal_tree(args: argparse.Namespace) -> None:
    if args.mode != "session-first":
        raise SystemExit("Unsupported mode. Use --mode session-first")

    conn = sqlite3.connect(Path(args.db_path))
    conn.row_factory = sqlite3.Row
    updated = 0
    buckets_count = 0

    try:
        conn.execute("BEGIN IMMEDIATE")
        ensure_agentic_schema(conn)
        rows = conn.execute(
            "SELECT id, content, metadata, tags, created_at, updated_at FROM memories ORDER BY id ASC"
        ).fetchall()
        memory_to_bucket, buckets = build_session_bucket_map(rows, args.merge_window_hours)
        buckets_count = len(buckets)

        for row in rows:
            memory_id = int(row["id"])
            metadata = json.loads(row["metadata"] or "{}")
            tags = json.loads(row["tags"] or "[]")
            if metadata.get("type") == "section":
                continue

            bucket = memory_to_bucket.get(memory_id, "unknown-session")
            path = causal_path_for_metadata(metadata, bucket)
            code = path[-1] if path else "9.9"
            section = extract_section(metadata)
            atomic = str(metadata.get("atomic_factor") or "causal-recompute")

            metadata["session_bucket"] = bucket
            metadata["causal_code"] = code
            metadata["causal_path"] = path
            metadata["causal_model"] = "session-first-v2"
            metadata["section"] = section

            tags = ensure_unique_list(
                ensure_tags(
                    [*tags, f"causal:{code}", f"session-bucket:{bucket}"],
                    section,
                    atomic,
                )
            )
            update_memory_record(
                conn,
                memory_id=memory_id,
                content=row["content"],
                metadata=metadata,
                tags=tags,
            )
            updated += 1

        conn.commit()
    finally:
        conn.close()

    print(
        json.dumps(
            {
                "status": "recomputed",
                "mode": args.mode,
                "merge_window_hours": args.merge_window_hours,
                "buckets": buckets_count,
                "memories_updated": updated,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def cmd_verify_integrity(args: argparse.Namespace) -> None:
    conn = sqlite3.connect(Path(args.db_path))
    conn.row_factory = sqlite3.Row
    issues: list[str] = []
    checks: dict[str, Any] = {}

    try:
        ensure_agentic_schema(conn)
        required_tables = [
            "memories",
            "memories_crossrefs",
            "agentic_event_registry",
            "agentic_section_registry",
            "agentic_canonical_registry",
            "agentic_atomic_registry",
            "agentic_cluster_edges",
        ]
        missing_tables = [t for t in required_tables if not table_exists(conn, t)]
        checks["missing_tables"] = missing_tables
        if missing_tables:
            issues.append(f"missing_tables={missing_tables}")

        orphan_atomic = conn.execute(
            """
            SELECT COUNT(*) FROM agentic_atomic_registry ar
            LEFT JOIN memories m ON m.id = ar.memory_id
            WHERE ar.memory_id IS NULL OR m.id IS NULL
            """
        ).fetchone()[0]
        checks["orphan_atomic_rows"] = orphan_atomic
        if orphan_atomic:
            issues.append(f"orphan_atomic_rows={orphan_atomic}")

        orphan_events = conn.execute(
            """
            SELECT COUNT(*) FROM agentic_event_registry er
            LEFT JOIN memories m ON m.id = er.memory_id
            WHERE er.memory_id IS NOT NULL AND m.id IS NULL
            """
        ).fetchone()[0]
        checks["orphan_event_rows"] = orphan_events
        if orphan_events:
            issues.append(f"orphan_event_rows={orphan_events}")

        invalid_cluster_primary = conn.execute(
            """
            SELECT COUNT(*) FROM memories
            WHERE json_extract(metadata, '$.cluster_primary') IS NOT NULL
              AND json_extract(metadata, '$.cluster_primary') NOT IN ({})
            """.format(",".join(["?"] * len(CANONICAL_CLUSTERS))),
            tuple(sorted(CANONICAL_CLUSTERS)),
        ).fetchone()[0]
        checks["invalid_cluster_primary"] = invalid_cluster_primary
        if invalid_cluster_primary:
            issues.append(f"invalid_cluster_primary={invalid_cluster_primary}")

        invalid_causal_path = conn.execute(
            """
            SELECT COUNT(*) FROM memories
            WHERE COALESCE(json_extract(metadata, '$.type'), '') != 'section'
              AND (
                json_type(metadata, '$.causal_path') IS NULL
                OR json_type(metadata, '$.causal_path') != 'array'
                OR COALESCE(json_array_length(json_extract(metadata, '$.causal_path')), 0) = 0
              )
            """
        ).fetchone()[0]
        checks["invalid_causal_path"] = invalid_causal_path
        if invalid_causal_path:
            issues.append(f"invalid_causal_path={invalid_causal_path}")

        invalid_causal_root = conn.execute(
            """
            SELECT COUNT(*) FROM memories
            WHERE COALESCE(json_extract(metadata, '$.type'), '') != 'section'
              AND COALESCE(json_extract(metadata, '$.causal_path[0]'), '') NOT IN ('0', '1', '5', '9')
            """
        ).fetchone()[0]
        checks["invalid_causal_root"] = invalid_causal_root
        if invalid_causal_root:
            issues.append(f"invalid_causal_root={invalid_causal_root}")

        missing_session_bucket = conn.execute(
            """
            SELECT COUNT(*) FROM memories
            WHERE COALESCE(json_extract(metadata, '$.type'), '') != 'section'
              AND COALESCE(json_extract(metadata, '$.session_bucket'), '') = ''
            """
        ).fetchone()[0]
        checks["missing_session_bucket"] = missing_session_bucket
        if missing_session_bucket:
            issues.append(f"missing_session_bucket={missing_session_bucket}")

        duplicate_rule_violations = 0
        rows = conn.execute("SELECT related FROM memories_crossrefs").fetchall()
        for row in rows:
            refs = parse_crossrefs_blob(row[0])
            for ref in refs:
                score = float(ref.get("score", 0.0))
                edge_type = str(ref.get("edge_type", "")).strip().lower()
                source = str(ref.get("source", "")).strip().lower()
                if score < 0.85:
                    continue
                is_allowed = (
                    edge_type in DUPLICATE_ALLOWED_EDGE_TYPES
                    or source in DUPLICATE_ALLOWED_SOURCES
                )
                if not is_allowed:
                    duplicate_rule_violations += 1
        checks["duplicate_rule_violations"] = duplicate_rule_violations
        if duplicate_rule_violations:
            issues.append(f"duplicate_rule_violations={duplicate_rule_violations}")

        status = "ok" if not issues else "failed"
        payload = {"status": status, "checks": checks, "issues": issues}
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        if args.strict and issues:
            raise SystemExit(1)
    finally:
        conn.close()


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
    cur.execute("SELECT COUNT(*) AS c FROM agentic_canonical_registry")
    canonical = cur.fetchone()["c"]
    cur.execute("SELECT COUNT(*) AS c FROM agentic_atomic_registry")
    atomic = cur.fetchone()["c"]
    cur.execute("SELECT COUNT(*) AS c FROM agentic_cluster_edges")
    cluster_edges = cur.fetchone()["c"]
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
                    "canonical_roots": canonical,
                    "atomic_segments": atomic,
                    "cluster_edges": cluster_edges,
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

    p_reset = sub.add_parser("reset-hard", help="Hard reset Memora DB and SSOT registries.")
    p_reset.add_argument(
        "--confirm",
        required=True,
        help=f"Mandatory confirmation token ({RESET_CONFIRM_TOKEN}).",
    )
    p_reset.set_defaults(func=cmd_reset_hard)

    p_ingest = sub.add_parser(
        "canonical-ingest",
        help="Parse canonical DSL and ingest atomic/idempotent segments.",
    )
    p_ingest.add_argument("--dsl", required=True, help="Path to canonical DSL file.")
    p_ingest.add_argument("--session-id", default=None, help="Session ID for session master clustering.")
    p_ingest.add_argument(
        "--session-state",
        choices=["start", "resume", "hidden"],
        default="start",
        help="Lifecycle state to map into session cluster.",
    )
    p_ingest.set_defaults(func=cmd_canonical_ingest)

    p_recompute = sub.add_parser(
        "recompute-clusters",
        help="Recompute cluster metadata and SSOT edge matrix.",
    )
    p_recompute.add_argument(
        "--mode",
        default="session-master",
        choices=["session-master"],
        help="Cluster recomputation mode.",
    )
    p_recompute.set_defaults(func=cmd_recompute_clusters)

    p_recompute_causal = sub.add_parser(
        "recompute-causal-tree",
        help="Recompute session-first causal taxonomy and session buckets.",
    )
    p_recompute_causal.add_argument(
        "--mode",
        default="session-first",
        choices=["session-first"],
        help="Causal recomputation mode.",
    )
    p_recompute_causal.add_argument(
        "--merge-window-hours",
        type=int,
        default=DEFAULT_CAUSAL_MERGE_WINDOW_HOURS,
        help="Window (hours) used to merge technical sessions into canonical session buckets.",
    )
    p_recompute_causal.set_defaults(func=cmd_recompute_causal_tree)

    p_verify = sub.add_parser(
        "verify-integrity",
        help="Validate SSOT idempotency, cluster integrity and duplicate policy.",
    )
    p_verify.add_argument(
        "--strict",
        action="store_true",
        help="Exit code 1 if any integrity issue is found.",
    )
    p_verify.set_defaults(func=cmd_verify_integrity)

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
