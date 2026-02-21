"""Graph data generation and transformation logic."""

import colorsys
import hashlib
import json
import os
import re
from datetime import datetime, timedelta
from importlib.metadata import version as get_version
from typing import Any, Dict, List, Optional


def _get_memora_version() -> str:
    try:
        return get_version("memora")
    except Exception:
        return ""

# Stale threshold for closed issues/TODOs (in days)
# Closed items older than this will appear gray and smaller
STALE_DAYS = int(os.getenv("MEMORA_STALE_DAYS", "30"))

from ..storage import (
    connect,
    detect_clusters,
    get_crossrefs,
    get_memory,
    list_memories,
    rebuild_crossrefs,
)
from .issues import (
    TAG_COLORS,
    build_status_to_nodes,
    build_issue_category_to_nodes,
    get_issue_node_style,
    is_issue,
    build_issue_legend_html,
)
from .todos import (
    build_todo_status_to_nodes,
    build_todo_category_to_nodes,
    get_todo_node_style,
    is_todo,
    build_todo_legend_html,
)
from .templates import build_static_html

# Similarity threshold for duplicate detection
DUPLICATE_THRESHOLD = 0.85
DUPLICATE_ALLOWED_EDGE_TYPES = {"related_to", "near_duplicate"}
DUPLICATE_ALLOWED_SOURCES = {"embedding_auto", "semantic_similarity"}

# Stale styling
STALE_COLOR = "#8b949e"  # Gray
STALE_SIZE_FACTOR = 0.7  # Reduce size to 70%


def _is_stale_closed(metadata: Optional[Dict], updated_at: Optional[str], created_at: Optional[str]) -> bool:
    """Check if a closed issue/TODO is stale (older than STALE_DAYS threshold).

    Uses updated_at if available, otherwise falls back to created_at.
    Only applies to closed issues/TODOs.
    """
    if not metadata:
        return False

    # Only check issues and TODOs that are closed
    mem_type = metadata.get("type")
    status = metadata.get("status")

    if mem_type not in ("issue", "todo"):
        return False
    if status != "closed":
        return False

    # Get the reference date (prefer updated_at, fall back to created_at)
    date_str = updated_at or created_at
    if not date_str:
        return False

    try:
        # Parse the date string (format: "2025-12-23 19:59:31")
        ref_date = datetime.strptime(date_str.split(".")[0], "%Y-%m-%d %H:%M:%S")
        threshold = datetime.now() - timedelta(days=STALE_DAYS)
        return ref_date < threshold
    except (ValueError, TypeError):
        return False


def _is_duplicate_eligible_reference(ref: Dict[str, Any]) -> bool:
    """Only semantic similarity edges should trigger duplicate signal."""
    edge_type = str(ref.get("edge_type", "")).strip()
    source = str(ref.get("source", "")).strip()
    explicit = ref.get("duplicate_eligible")
    if isinstance(explicit, bool):
        return explicit
    return edge_type in DUPLICATE_ALLOWED_EDGE_TYPES or source in DUPLICATE_ALLOWED_SOURCES


def is_section(metadata: Optional[Dict]) -> bool:
    """Check if a memory is a section header based on metadata."""
    if not metadata:
        return False
    return metadata.get("type") == "section"


def _find_duplicate_ids(conn, memories: List[Dict]) -> set:
    """Find memory IDs that have duplicates (similarity >= threshold).

    A memory is marked as duplicate if it has a cross-reference with
    score >= DUPLICATE_THRESHOLD to another memory in the current view.
    Section memories are excluded from duplicate detection.
    """
    # Exclude section memories from duplicate detection
    non_section_memories = [m for m in memories if not is_section(m.get("metadata"))]
    memory_ids = {m["id"] for m in non_section_memories}
    duplicate_ids = set()

    for m in non_section_memories:
        for ref in get_crossrefs(conn, m["id"]):
            if not _is_duplicate_eligible_reference(ref):
                continue
            if ref.get("score", 0) >= DUPLICATE_THRESHOLD:
                # Only mark if the related memory is also in our view
                if ref["id"] in memory_ids:
                    duplicate_ids.add(m["id"])
                    duplicate_ids.add(ref["id"])

    return duplicate_ids


def _expand_r2_urls(metadata: Optional[Dict]) -> Dict:
    """Expand R2 URLs in metadata for display."""
    if not metadata:
        return {}

    meta = dict(metadata)
    if meta.get("images"):
        from ..image_storage import expand_r2_url

        expanded_images = []
        for img in meta["images"]:
            if isinstance(img, dict) and img.get("src"):
                src = img["src"]
                if src.startswith("r2://") or src.startswith("/r2/"):
                    src = expand_r2_url(
                        src.replace("/r2/", "r2://") if src.startswith("/r2/") else src,
                        use_proxy=True,
                    )
                expanded_images.append({**img, "src": src})
            else:
                expanded_images.append(img)
        meta["images"] = expanded_images

    return meta


def _stable_color_from_tag(tag: str) -> str:
    """Generate a deterministic, semantically meaningful color for a tag."""
    if tag == "untagged":
        return "#6e7681"

    semantic_palette = {
        "section:delivery": "#f59e0b",
        "section:analysis": "#3b82f6",
        "section:implementation": "#22c55e",
        "section:governance": "#a855f7",
        "section:session": "#ec4899",
        "section:platform": "#14b8a6",
        "section:memory": "#06b6d4",
        "atomic": "#0ea5e9",
        "agentic": "#22c55e",
        "memora": "#14b8a6",
        "hitl": "#f97316",
        "tracking": "#6366f1",
        "delivery": "#f59e0b",
        "checkpoint": "#3b82f6",
        "code-change": "#10b981",
    }

    semantic_key = None
    if tag.startswith("section:"):
        root = tag.split(":", 1)[1].split("/", 1)[0]
        semantic_key = f"section:{root}"
    elif tag.startswith("atomic:"):
        semantic_key = "atomic"
    else:
        semantic_key = tag

    base = semantic_palette.get(semantic_key)
    if base:
        return base

    # Fallback: deterministic hue for unknown classes/tags.
    digest = hashlib.sha1(tag.encode("utf-8")).digest()
    hue = digest[0] / 255.0
    saturation = 0.58 + ((digest[1] / 255.0) * 0.22)  # 0.58 - 0.80
    lightness = 0.46 + ((digest[2] / 255.0) * 0.14)  # 0.46 - 0.60
    red, green, blue = colorsys.hls_to_rgb(hue, lightness, saturation)
    return "#{:02x}{:02x}{:02x}".format(int(red * 255), int(green * 255), int(blue * 255))


def _build_tag_colors(memories: List[Dict]) -> Dict[str, str]:
    """Build tag -> color mapping from memories."""
    tag_colors = {}
    for m in memories:
        tags = m.get("tags", [])
        primary_tag = tags[0] if tags else "untagged"
        if primary_tag not in tag_colors:
            tag_colors[primary_tag] = _stable_color_from_tag(primary_tag)
    return tag_colors


def _count_connections(edges: List[Dict]) -> Dict[int, int]:
    """Count connections per node from edge list."""
    counts: Dict[int, int] = {}
    for edge in edges:
        from_id = edge["from"]
        to_id = edge["to"]
        counts[from_id] = counts.get(from_id, 0) + 1
        counts[to_id] = counts.get(to_id, 0) + 1
    return counts


def _build_nodes(
    memories: List[Dict],
    tag_colors: Dict[str, str],
    connection_counts: Optional[Dict[int, int]] = None,
    duplicate_ids: Optional[set] = None,
) -> List[Dict]:
    """Build vis.js node objects from memories.

    Section memories are excluded from the graph.
    """
    import math

    if duplicate_ids is None:
        duplicate_ids = set()

    nodes = []
    for m in memories:
        # Skip section memories - they are not visible in the graph
        if is_section(m.get("metadata")):
            continue
        tags = m.get("tags", [])
        primary_tag = tags[0] if tags else "untagged"
        meta = m.get("metadata") or {}
        session_id = meta.get("session_id") or meta.get("session") or meta.get("sessionId")
        visibility = str(meta.get("visibility") or "active")
        cluster_primary = str(meta.get("cluster_primary") or "")
        cluster_secondary = meta.get("cluster_secondary") if isinstance(meta.get("cluster_secondary"), list) else []

        content = m["content"]
        # Get first line or first 60 chars for headline, strip markdown headers
        first_line = content.split("\n")[0].lstrip("#").strip()[:60]
        headline = first_line.replace('"', "'").replace("\\", "")
        label = content[:35].replace("\n", " ").replace("#", "").replace("*", "").replace("_", "").replace("`", "").replace("[", "").replace("]", "").strip().replace('"', "'").replace("\\", "")

        # Calculate node size based on connections (like Connected Papers)
        connections = connection_counts.get(m["id"], 0) if connection_counts else 0
        # Use logarithmic scaling: base size 12, grows with connections
        # Min size 12, max size ~40
        node_size = 12 + min(28, int(math.log1p(connections) * 8))
        # Mass affects physics: higher mass = more central, lower mass = pushed to edges
        # Nodes with 0 connections have mass 0.5, highly connected nodes up to mass 3
        node_mass = 0.5 + min(2.5, math.log1p(connections) * 0.8)

        # Build title with type indicator
        type_label = ""
        if is_issue(meta):
            type_label = " - Issue"
        elif is_todo(meta):
            type_label = " - TODO"

        node = {
            "id": m["id"],
            "label": label + "..." if len(content) > 35 else label,
            "title": f"#{m['id']}{type_label}\n{headline}",
            "color": tag_colors[primary_tag],
            "size": node_size,
            "mass": node_mass,
            "degree": connections,
            "session": session_id,
            "visibility": visibility,
            "clusterPrimary": cluster_primary,
            "clusterSecondary": cluster_secondary,
        }

        # Apply issue-specific styling
        issue_style = get_issue_node_style(meta)
        if issue_style:
            node.update(issue_style)

        # Apply TODO-specific styling
        todo_style = get_todo_node_style(meta)
        if todo_style:
            node.update(todo_style)

        # Apply duplicate indicator - red border
        if m["id"] in duplicate_ids:
            node["color"] = {
                "background": node.get("color", "#a855f7"),
                "border": "#f85149",
            }
            node["borderWidth"] = 3

        # Apply stale styling for old closed issues/TODOs
        if _is_stale_closed(meta, m.get("updated_at"), m.get("created_at")):
            node["color"] = STALE_COLOR
            node["size"] = int(node.get("size", 12) * STALE_SIZE_FACTOR)

        nodes.append(node)

    return nodes


def _build_tag_to_nodes(memories: List[Dict]) -> Dict[str, List[int]]:
    """Build tag -> node IDs mapping. Section memories are excluded."""
    tag_to_nodes: Dict[str, List[int]] = {}
    for m in memories:
        # Skip section memories - they're not visible in graph
        if is_section(m.get("metadata")):
            continue
        for tag in m.get("tags", []):
            if tag not in tag_to_nodes:
                tag_to_nodes[tag] = []
            tag_to_nodes[tag].append(m["id"])
    return tag_to_nodes


def _build_node_tags(memories: List[Dict]) -> Dict[str, List[str]]:
    node_tags: Dict[str, List[str]] = {}
    for m in memories:
        if is_section(m.get("metadata")):
            continue
        tags = [str(t) for t in (m.get("tags") or []) if str(t)]
        node_tags[str(m["id"])] = tags
    return node_tags


def _build_section_mappings(memories: List[Dict]) -> tuple:
    """Build section and subsection -> node IDs mappings.

    Returns (section_to_nodes, path_to_nodes) tuple.
    Issues, TODOs, and section placeholders are excluded.
    """
    section_to_nodes: Dict[str, List[int]] = {}
    path_to_nodes: Dict[str, List[int]] = {}

    for m in memories:
        meta = m.get("metadata") or {}

        # Skip issues, TODOs, and section placeholders
        if is_issue(meta) or is_todo(meta) or is_section(meta):
            continue

        hierarchy = meta.get("hierarchy", {})
        hierarchy_path = hierarchy.get("path", []) if isinstance(hierarchy, dict) else []

        if hierarchy_path and len(hierarchy_path) >= 1:
            section = hierarchy_path[0]
            parts = hierarchy_path[1:]
        else:
            section = meta.get("section", "Uncategorized")
            subsection = meta.get("subsection", "")
            parts = subsection.split("/") if subsection else []

        if section not in section_to_nodes:
            section_to_nodes[section] = []
        section_to_nodes[section].append(m["id"])

        if parts:
            for i in range(len(parts)):
                partial_path = "/".join(parts[: i + 1])
                full_key = f"{section}/{partial_path}"
                if full_key not in path_to_nodes:
                    path_to_nodes[full_key] = []
                path_to_nodes[full_key].append(m["id"])

    return section_to_nodes, path_to_nodes


def _build_session_mappings(memories: List[Dict]) -> Dict[str, List[int]]:
    """Build session_id -> node IDs mapping."""
    session_to_nodes: Dict[str, List[int]] = {}
    for m in memories:
        if is_section(m.get("metadata")):
            continue
        meta = m.get("metadata") or {}
        session_id = meta.get("session_id") or meta.get("session") or meta.get("sessionId")
        if not session_id:
            continue
        session_to_nodes.setdefault(str(session_id), []).append(m["id"])
    return session_to_nodes


def _build_edges(conn, memories: List[Dict], min_score: float) -> List[Dict]:
    """Build vis.js edge objects from crossrefs."""
    edges = []
    seen = set()
    edge_id = 0
    for m in memories:
        for ref in get_crossrefs(conn, m["id"]):
            edge_key = tuple(sorted([m["id"], ref["id"]]))
            if edge_key not in seen and ref.get("score", 0) > min_score:
                seen.add(edge_key)
                edges.append(
                    {
                        "id": edge_id,
                        "from": m["id"],
                        "to": ref["id"],
                        "edge_type": ref.get("edge_type"),
                        "source": ref.get("source"),
                        "score": ref.get("score", 0),
                        "duplicate_eligible": _is_duplicate_eligible_reference(ref),
                    }
                )
                edge_id += 1
    return edges


def _build_ssot_cluster_state(memories: List[Dict]) -> Dict[str, Any]:
    project_master: Dict[str, Any] = {}
    session_masters: Dict[str, List[int]] = {}
    session_master_clusters: Dict[str, List[int]] = {}
    subclusters_by_session: Dict[str, Dict[str, List[int]]] = {}
    node_primary_cluster: Dict[str, str] = {}
    node_secondary_clusters: Dict[str, List[str]] = {}
    hidden_node_ids: List[int] = []

    latest_project_dt: Optional[datetime] = None

    for m in memories:
        meta = m.get("metadata") or {}
        if is_section(meta):
            continue

        memory_id = int(m["id"])
        session_id = str(meta.get("session_id") or meta.get("session") or meta.get("sessionId") or "")
        primary = str(meta.get("cluster_primary") or "")
        secondaries = meta.get("cluster_secondary") if isinstance(meta.get("cluster_secondary"), list) else []
        visibility = str(meta.get("visibility") or "active")

        if not primary:
            tags = m.get("tags", []) or []
            cluster_tag = next((t for t in tags if isinstance(t, str) and t.startswith("cluster:")), None)
            if cluster_tag:
                primary = cluster_tag.split(":", 1)[1]
        if not primary:
            primary = "ws.plan"

        node_primary_cluster[str(memory_id)] = primary
        node_secondary_clusters[str(memory_id)] = [str(x) for x in secondaries if str(x) and str(x) != primary]

        if visibility == "hidden":
            hidden_node_ids.append(memory_id)

        if session_id:
            session_masters.setdefault(session_id, []).append(memory_id)
            subclusters_by_session.setdefault(session_id, {}).setdefault(primary, []).append(memory_id)
            if primary == "session.master":
                session_master_clusters.setdefault(session_id, []).append(memory_id)

        canonical = meta.get("canonical") if isinstance(meta.get("canonical"), dict) else {}
        pkey = canonical.get("project_master_key")
        if pkey:
            ts = _parse_graph_timestamp(m.get("updated_at") or m.get("created_at"))
            if ts and (latest_project_dt is None or ts > latest_project_dt):
                latest_project_dt = ts
                project_master = {
                    "memoryId": memory_id,
                    "projectMasterKey": pkey,
                    "payloadHash": canonical.get("payload_hash"),
                    "idempotencyKey": canonical.get("idempotency_key"),
                    "o_opp": canonical.get("o_opp"),
                    "v_vdd": canonical.get("v_vdd"),
                }

    return {
        "projectMaster": project_master,
        "sessionMasters": session_masters,
        "sessionMasterClusters": session_master_clusters,
        "subclustersBySession": subclusters_by_session,
        "nodePrimaryCluster": node_primary_cluster,
        "nodeSecondaryClusters": node_secondary_clusters,
        "hiddenNodeIds": sorted(hidden_node_ids),
        "duplicateRule": {
            "threshold": DUPLICATE_THRESHOLD,
            "allowed_edge_types": sorted(DUPLICATE_ALLOWED_EDGE_TYPES),
            "allowed_sources": sorted(DUPLICATE_ALLOWED_SOURCES),
            "policy": "semantic_only",
        },
    }


def _build_timeline_data(memories: List[Dict]) -> tuple:
    """Build timeline data from memories.

    Returns:
        (node_timestamps, min_date, max_date) tuple
        - node_timestamps: dict mapping node ID to created_at timestamp
        - min_date: earliest date string
        - max_date: latest date string
    """
    node_timestamps: Dict[int, str] = {}
    dates = []

    for m in memories:
        # Skip section memories
        if is_section(m.get("metadata")):
            continue

        created_at = m.get("created_at")
        if created_at:
            node_timestamps[m["id"]] = created_at
            dates.append(created_at)

    if not dates:
        return {}, "", ""

    dates.sort()
    return node_timestamps, dates[0], dates[-1]


def _parse_graph_timestamp(ts: Optional[str]) -> Optional[datetime]:
    """Parse graph timestamp formats used by memora storage."""
    if not ts:
        return None
    try:
        return datetime.strptime(ts.split(".")[0], "%Y-%m-%d %H:%M:%S")
    except Exception:
        return None


def _build_latest_memory(memories: List[Dict]) -> Optional[Dict[str, Any]]:
    """Return metadata for the latest non-section memory in the graph."""
    latest: Optional[Dict[str, Any]] = None
    latest_dt: Optional[datetime] = None

    for m in memories:
        # Keep consistent with visible graph nodes.
        if is_section(m.get("metadata")):
            continue

        updated_at = m.get("updated_at")
        created_at = m.get("created_at")
        effective_ts = updated_at or created_at
        ts_dt = _parse_graph_timestamp(effective_ts)
        if ts_dt is None:
            continue

        if latest_dt is None or ts_dt > latest_dt or (ts_dt == latest_dt and m["id"] > latest["id"]):
            tags = m.get("tags", [])
            primary_tag = tags[0] if tags else "untagged"
            meta = m.get("metadata") or {}
            hierarchy = meta.get("hierarchy", {})
            hierarchy_path = hierarchy.get("path", []) if isinstance(hierarchy, dict) else []
            section = hierarchy_path[0] if hierarchy_path else meta.get("section")

            headline = (m.get("content") or "").split("\n")[0].lstrip("#").strip()[:80]
            latest_dt = ts_dt
            latest = {
                "id": m["id"],
                "created": created_at,
                "updated": updated_at,
                "effective": effective_ts,
                "primaryTag": primary_tag,
                "section": section,
                "headline": headline,
            }

    return latest


CLUSTER_COLORS = [
    "#ff6b6b", "#ffd93d", "#6bcb77", "#4d96ff",
    "#ff922b", "#cc5de8", "#20c997", "#339af0",
    "#f06595", "#a9e34b", "#22b8cf", "#845ef7",
]

SESSION_BUCKET_WINDOW_HOURS = int(os.getenv("MEMORA_SESSION_BUCKET_WINDOW_HOURS", "4"))
CAUSAL_TOP_LEVEL_ORDER = {"0": 0, "1": 1, "5": 2, "9": 3}
CAUSAL_LABELS = {
    "0": "Sessions",
    "1": "Implementation",
    "1.2": "Delivery",
    "1.4": "Features",
    "5": "Status",
    "5.1": "Release",
    "5.2": "Closure",
    "5.3": "General",
    "9": "Operations",
    "9.0": "Operations",
    "9.1": "Analysis",
    "9.2": "Governance",
    "9.3": "Memory",
    "9.4": "Platform",
    "9.9": "Uncategorized",
}


def _slug_token(value: str) -> str:
    token = re.sub(r"[^a-z0-9]+", "-", str(value or "").strip().lower()).strip("-")
    return token or "general"


def _title_token(value: str) -> str:
    clean = str(value or "").replace("-", " ").replace("_", " ").strip()
    return clean.title() if clean else "General"


def _effective_timestamp(memory: Dict[str, Any]) -> Optional[datetime]:
    return _parse_graph_timestamp(memory.get("updated_at") or memory.get("created_at"))


def _extract_section(metadata: Dict[str, Any]) -> str:
    hierarchy = metadata.get("hierarchy", {})
    hierarchy_path = hierarchy.get("path", []) if isinstance(hierarchy, dict) else []
    if hierarchy_path and len(hierarchy_path) >= 1:
        head = str(hierarchy_path[0]).strip("/")
        tail = "/".join(str(x).strip("/") for x in hierarchy_path[1:] if str(x).strip("/"))
        return f"{head}/{tail}".strip("/") if tail else head
    section = str(metadata.get("section") or "").strip("/")
    subsection = str(metadata.get("subsection") or "").strip("/")
    if section and subsection:
        return f"{section}/{subsection}".strip("/")
    if section:
        return section
    return "uncategorized"


def _resolve_causal_path(metadata: Dict[str, Any], session_bucket: str) -> List[tuple[str, str]]:
    section = _extract_section(metadata).lower()
    cluster_primary = str(metadata.get("cluster_primary") or "").lower()

    # Session-first branch
    if (
        cluster_primary.startswith("session.")
        or section.startswith("session/")
        or section == "session"
    ):
        bucket_code = f"0.{_slug_token(session_bucket or 'unknown')}"
        bucket_label = f"Session {session_bucket or 'unknown'}"
        return [("0", CAUSAL_LABELS["0"]), (bucket_code, bucket_label)]

    # Implementation branch
    if section.startswith("implementation/"):
        sub = _slug_token(section.split("/", 1)[1])
        return [
            ("1", CAUSAL_LABELS["1"]),
            (f"1.{sub}", f"Implementation/{_title_token(sub)}"),
        ]

    # Delivery grouped into implementation/features and status
    if section == "delivery/pilot":
        return [
            ("1", CAUSAL_LABELS["1"]),
            ("1.2", CAUSAL_LABELS["1.2"]),
            ("1.2.pilot", "Pilot"),
        ]
    if section in {"delivery/features", "delivery/graph"}:
        sub = _slug_token(section.split("/", 1)[1])
        return [
            ("1", CAUSAL_LABELS["1"]),
            ("1.4", CAUSAL_LABELS["1.4"]),
            (f"1.4.{sub}", _title_token(sub)),
        ]
    if section == "delivery/release":
        return [("5", CAUSAL_LABELS["5"]), ("5.1", CAUSAL_LABELS["5.1"])]
    if section == "delivery/closure":
        return [("5", CAUSAL_LABELS["5"]), ("5.2", CAUSAL_LABELS["5.2"])]
    if section == "delivery/status":
        return [("5", CAUSAL_LABELS["5"]), ("5.3", CAUSAL_LABELS["5.3"])]

    # Operations split
    if section.startswith("analysis/"):
        sub = _slug_token(section.split("/", 1)[1])
        return [
            ("9", CAUSAL_LABELS["9"]),
            ("9.1", CAUSAL_LABELS["9.1"]),
            (f"9.1.{sub}", _title_token(sub)),
        ]
    if section.startswith("governance/") or section == "governance":
        sub = _slug_token(section.split("/", 1)[1] if "/" in section else "general")
        return [
            ("9", CAUSAL_LABELS["9"]),
            ("9.2", CAUSAL_LABELS["9.2"]),
            (f"9.2.{sub}", _title_token(sub)),
        ]
    if section.startswith("memory"):
        return [("9", CAUSAL_LABELS["9"]), ("9.3", CAUSAL_LABELS["9.3"])]
    if section.startswith("platform"):
        return [("9", CAUSAL_LABELS["9"]), ("9.4", CAUSAL_LABELS["9.4"])]
    if section.startswith("operations"):
        return [("9", CAUSAL_LABELS["9"]), ("9.0", CAUSAL_LABELS["9.0"])]

    return [("9", CAUSAL_LABELS["9"]), ("9.9", CAUSAL_LABELS["9.9"])]


def _causal_sort_key(code: str) -> tuple:
    text = str(code or "")
    top = text.split(".", 1)[0]
    top_order = CAUSAL_TOP_LEVEL_ORDER.get(top, 99)
    parts = text.split(".")
    normalized = []
    for p in parts:
        if p.isdigit():
            normalized.append((0, int(p)))
        else:
            normalized.append((1, p))
    return (top_order, tuple(normalized), text)


def _build_session_buckets(memories: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], Dict[str, str], Dict[str, str]]:
    sessions: Dict[str, Dict[str, Any]] = {}
    for m in memories:
        meta = m.get("metadata") or {}
        if is_section(meta):
            continue
        session_id = str(meta.get("session_id") or meta.get("session") or meta.get("sessionId") or "unknown-session")
        ts = _effective_timestamp(m)
        entry = sessions.setdefault(
            session_id,
            {
                "sessionId": session_id,
                "start": None,
                "end": None,
                "nodeIds": [],
            },
        )
        entry["nodeIds"].append(int(m["id"]))
        if ts:
            entry["start"] = ts if entry["start"] is None or ts < entry["start"] else entry["start"]
            entry["end"] = ts if entry["end"] is None or ts > entry["end"] else entry["end"]

    ordered = sorted(
        sessions.values(),
        key=lambda item: (
            item["start"] is None,
            item["start"] or datetime.min,
            item["sessionId"],
        ),
    )

    buckets: List[Dict[str, Any]] = []
    session_to_bucket: Dict[str, str] = {}
    node_to_bucket: Dict[str, str] = {}
    merge_window = timedelta(hours=max(1, SESSION_BUCKET_WINDOW_HOURS))

    used_bucket_ids: set[str] = set()

    def _new_bucket(rec: Dict[str, Any]) -> Dict[str, Any]:
        start = rec["start"]
        base = start.strftime("%Y%m%d-%H%M") if start else f"unknown-{_slug_token(rec['sessionId'])[:8]}"
        bucket_id = base
        n = 1
        while bucket_id in used_bucket_ids:
            n += 1
            bucket_id = f"{base}-{n}"
        used_bucket_ids.add(bucket_id)
        return {
            "bucketId": bucket_id,
            "shortLabel": bucket_id,
            "start": rec["start"],
            "end": rec["end"],
            "sessionIds": [rec["sessionId"]],
            "nodeIds": list(rec["nodeIds"]),
        }

    current: Optional[Dict[str, Any]] = None
    for rec in ordered:
        if current is None:
            current = _new_bucket(rec)
            buckets.append(current)
            continue

        can_merge = (
            rec["start"] is not None
            and current["end"] is not None
            and rec["start"] - current["end"] <= merge_window
        )
        if can_merge:
            current["sessionIds"].append(rec["sessionId"])
            current["nodeIds"].extend(rec["nodeIds"])
            if rec["end"] and (current["end"] is None or rec["end"] > current["end"]):
                current["end"] = rec["end"]
            if rec["start"] and (current["start"] is None or rec["start"] < current["start"]):
                current["start"] = rec["start"]
        else:
            current = _new_bucket(rec)
            buckets.append(current)

    for bucket in buckets:
        bucket["nodeIds"] = sorted(set(int(x) for x in bucket["nodeIds"]))
        for sid in bucket["sessionIds"]:
            session_to_bucket[sid] = bucket["bucketId"]
        for nid in bucket["nodeIds"]:
            node_to_bucket[str(nid)] = bucket["bucketId"]

    output = []
    for bucket in buckets:
        output.append(
            {
                "bucketId": bucket["bucketId"],
                "shortLabel": bucket["shortLabel"],
                "startAt": bucket["start"].strftime("%Y-%m-%d %H:%M:%S") if bucket["start"] else None,
                "endAt": bucket["end"].strftime("%Y-%m-%d %H:%M:%S") if bucket["end"] else None,
                "sessionIds": bucket["sessionIds"],
                "nodeIds": bucket["nodeIds"],
                "memoryCount": len(bucket["nodeIds"]),
            }
        )
    return output, session_to_bucket, node_to_bucket


def _build_causal_state(
    memories: List[Dict[str, Any]],
    node_primary_cluster: Dict[str, str],
    tag_to_nodes: Dict[str, List[int]],
) -> Dict[str, Any]:
    session_buckets, session_to_bucket, node_to_bucket = _build_session_buckets(memories)

    tree_nodes: Dict[str, Dict[str, Any]] = {}
    node_causal_path: Dict[str, List[str]] = {}
    node_causal_leaf: Dict[str, str] = {}
    node_section: Dict[str, str] = {}

    def ensure_tree_node(code: str, label: str, parent: Optional[str]) -> None:
        if code not in tree_nodes:
            tree_nodes[code] = {
                "id": code,
                "code": code,
                "label": label,
                "count": 0,
                "nodeIds": set(),
                "children": set(),
                "parent": parent,
            }
        if parent:
            ensure_tree_node(parent, CAUSAL_LABELS.get(parent, parent), None if "." not in parent else parent.rsplit(".", 1)[0])
            tree_nodes[parent]["children"].add(code)

    # Ensure top-level trunk exists even if empty.
    for top in ("0", "1", "5", "9"):
        ensure_tree_node(top, CAUSAL_LABELS.get(top, top), None)

    for m in memories:
        meta = m.get("metadata") or {}
        if is_section(meta):
            continue
        memory_id = int(m["id"])
        memory_key = str(memory_id)
        section = _extract_section(meta)
        node_section[memory_key] = section
        session_id = str(meta.get("session_id") or meta.get("session") or meta.get("sessionId") or "unknown-session")
        bucket = node_to_bucket.get(memory_key) or session_to_bucket.get(session_id) or "unknown-session"

        causal_path = _resolve_causal_path(meta, bucket)
        node_causal_path[memory_key] = [code for code, _ in causal_path]
        node_causal_leaf[memory_key] = causal_path[-1][0]

        parent = None
        for code, label in causal_path:
            ensure_tree_node(code, label, parent)
            tree_nodes[code]["count"] += 1
            tree_nodes[code]["nodeIds"].add(memory_id)
            parent = code

    def build_tree(code: str) -> Dict[str, Any]:
        node = tree_nodes[code]
        children = sorted(node["children"], key=_causal_sort_key)
        return {
            "id": node["id"],
            "code": node["code"],
            "label": node["label"],
            "count": node["count"],
            "nodeIds": sorted(node["nodeIds"]),
            "children": [build_tree(child) for child in children],
        }

    top_level = sorted([k for k, n in tree_nodes.items() if n["parent"] is None], key=_causal_sort_key)
    causal_tree = [build_tree(code) for code in top_level]

    # Facets
    facet_clusters: Dict[str, int] = {}
    for cluster in node_primary_cluster.values():
        key = str(cluster or "unassigned")
        facet_clusters[key] = facet_clusters.get(key, 0) + 1

    facet_sections: Dict[str, int] = {}
    for section in node_section.values():
        facet_sections[section] = facet_sections.get(section, 0) + 1

    facet_sessions: Dict[str, int] = {}
    for bucket in node_to_bucket.values():
        facet_sessions[bucket] = facet_sessions.get(bucket, 0) + 1

    facet_tags: Dict[str, int] = {}
    for tag, ids in tag_to_nodes.items():
        facet_tags[tag] = len(ids)

    facet_causal: Dict[str, int] = {}
    for code in node_causal_leaf.values():
        facet_causal[code] = facet_causal.get(code, 0) + 1

    # Stable coordinates for flat organogram.
    bucket_order = [item["bucketId"] for item in session_buckets]
    if "unknown-session" in node_to_bucket.values() and "unknown-session" not in bucket_order:
        bucket_order.append("unknown-session")

    leaf_codes = sorted(set(node_causal_leaf.values()), key=_causal_sort_key)
    rank_index = {code: idx for idx, code in enumerate(leaf_codes)}
    bucket_index = {bid: idx for idx, bid in enumerate(bucket_order)}
    grouped: Dict[tuple[str, str], List[int]] = {}
    for sid, bucket in node_to_bucket.items():
        leaf = node_causal_leaf.get(sid, "9.9")
        grouped.setdefault((bucket, leaf), []).append(int(sid))
    coords: Dict[str, Dict[str, float]] = {}
    for (bucket, leaf), ids in grouped.items():
        ids = sorted(ids)
        x0 = bucket_index.get(bucket, len(bucket_index)) * 380
        y0 = rank_index.get(leaf, len(rank_index)) * 190
        for idx, mid in enumerate(ids):
            coords[str(mid)] = {
                "x": float(x0 + (idx % 3) * 36),
                "y": float(y0 + (idx // 3) * 36),
            }

    return {
        "causalTree": causal_tree,
        "sessionBuckets": session_buckets,
        "nodeCausalPath": node_causal_path,
        "nodeCausalLeaf": node_causal_leaf,
        "nodeSessionBucket": node_to_bucket,
        "nodeSection": node_section,
        "facetCounts": {
            "clusters": facet_clusters,
            "sections": facet_sections,
            "sessions": facet_sessions,
            "tags": facet_tags,
            "causal": facet_causal,
        },
        "layoutMeta": {
            "mode": "organogram-flat",
            "stable": True,
            "bucketOrder": bucket_order,
            "rankOrder": leaf_codes,
            "coords": coords,
        },
    }


def _build_cluster_data(
    conn, memories: List[Dict], min_score: float = 0.5
) -> Dict[str, Any]:
    """Build cluster mappings using Louvain community detection.

    Returns dict with clusterToNodes, nodeToCluster, clusterColors, clusterMeta.
    """
    # Filter out section memories
    non_section_ids = [
        m["id"] for m in memories if not is_section(m.get("metadata"))
    ]

    clusters = detect_clusters(
        conn, min_cluster_size=3, min_score=min_score, algorithm="louvain"
    )

    if not clusters:
        return {
            "clusterToNodes": {},
            "nodeToCluster": {},
            "clusterColors": {},
            "clusterMeta": {},
        }

    cluster_to_nodes: Dict[str, List[int]] = {}
    node_to_cluster: Dict[str, int] = {}
    cluster_colors: Dict[str, str] = {}
    cluster_meta: Dict[str, Dict] = {}

    non_section_set = set(non_section_ids)

    for c in clusters:
        cid = str(c["cluster_id"])
        # Only include non-section memories that are in the graph
        members = [mid for mid in c["memory_ids"] if mid in non_section_set]
        if len(members) < 3:
            continue

        cluster_to_nodes[cid] = members
        color = CLUSTER_COLORS[(c["cluster_id"] - 1) % len(CLUSTER_COLORS)]
        cluster_colors[cid] = color

        for mid in members:
            node_to_cluster[str(mid)] = c["cluster_id"]

        # Build a human-readable label from top tags
        label_tags = [t for t in c.get("top_tags", []) if "/" not in t][:2]
        if not label_tags:
            label_tags = [t.split("/")[-1] for t in c.get("top_tags", [])[:2]]
        label = ", ".join(label_tags) if label_tags else f"Cluster {cid}"

        cluster_meta[cid] = {
            "size": len(members),
            "top_tags": c.get("top_tags", []),
            "label": label,
        }

    return {
        "clusterToNodes": cluster_to_nodes,
        "nodeToCluster": node_to_cluster,
        "clusterColors": cluster_colors,
        "clusterMeta": cluster_meta,
    }


def _build_cluster_legend_html(
    cluster_meta: Dict[str, Dict], cluster_colors: Dict[str, str]
) -> str:
    """Build HTML for cluster legend panel."""
    html = ""
    for cid, meta in cluster_meta.items():
        color = cluster_colors.get(cid, "#8b949e")
        label = meta["label"]
        size = meta["size"]
        html += (
            f'<div class="cluster-item" data-cluster="{cid}" '
            f"onclick=\"filterByCluster('{cid}')\">"
            f'<span class="cluster-color" style="background:{color}"></span>'
            f"{label} ({size})</div>"
        )
    if cluster_meta:
        html += '<label class="hull-toggle"><input type="checkbox" onchange="toggleClusterHulls(this)"> Show boundaries</label>'
    return html


def _build_legend_html(tag_colors: Dict[str, str]) -> str:
    """Build HTML for tag legend."""
    return "".join(
        f'<div class="legend-item" data-tag="{t}" onclick="filterByTag(\'{t}\')">'
        f'<span class="legend-color" style="background:{c}"></span>{t}</div>'
        for t, c in list(tag_colors.items())[:12]
    )


def _build_sections_html(
    section_to_nodes: Dict[str, List[int]], path_to_nodes: Dict[str, List[int]]
) -> str:
    """Build HTML for sections hierarchy."""
    sections_html = ""
    for section, node_ids in section_to_nodes.items():
        sections_html += (
            f'<div class="section-item" data-section="{section}" '
            f"onclick=\"filterBySection('{section}')\">{section} ({len(node_ids)})</div>"
        )

        section_paths = sorted(
            [k for k in path_to_nodes.keys() if k.startswith(section + "/")]
        )
        rendered_paths = set()

        for full_path in section_paths:
            sub_path = full_path[len(section) + 1 :]
            parts = sub_path.split("/")

            for i, part in enumerate(parts):
                partial = "/".join(parts[: i + 1])
                render_key = f"{section}/{partial}"

                if render_key not in rendered_paths:
                    rendered_paths.add(render_key)
                    indent = "&nbsp;&nbsp;" * i
                    count = len(path_to_nodes.get(render_key, []))
                    sections_html += (
                        f'<div class="subsection-item" data-subsection="{render_key}" '
                        f"onclick=\"filterBySubsection('{render_key}')\" "
                        f'style="padding-left:{8 + i*12}px;">{indent}└ {part} ({count})</div>'
                    )

    return sections_html


def get_graph_data(min_score: float = 0.40, rebuild: bool = False) -> Dict[str, Any]:
    """Get graph nodes, edges, and metadata for API response.

    Args:
        min_score: Minimum similarity score for edges
        rebuild: If True, rebuild crossrefs (slow). If False, use existing.

    Returns:
        Dict with nodes, edges, and various mappings.
    """
    conn = connect()
    try:
        memories = list_memories(conn, None, None, None, 0, None, None, None, None, None)
        if not memories:
            return {"error": "no_memories", "message": "No memories to visualize"}

        if rebuild:
            rebuild_crossrefs(conn)

        # Build edges first to calculate connection counts for node sizing
        edges = _build_edges(conn, memories, min_score)
        connection_counts = _count_connections(edges)

        # Find duplicates (similarity >= 0.7)
        duplicate_ids = _find_duplicate_ids(conn, memories)

        tag_colors = _build_tag_colors(memories)
        nodes = _build_nodes(memories, tag_colors, connection_counts, duplicate_ids)
        tag_to_nodes = _build_tag_to_nodes(memories)
        node_tags = _build_node_tags(memories)
        section_to_nodes, path_to_nodes = _build_section_mappings(memories)
        session_to_nodes = _build_session_mappings(memories)
        status_to_nodes = build_status_to_nodes(memories)
        issue_category_to_nodes = build_issue_category_to_nodes(memories)
        todo_status_to_nodes = build_todo_status_to_nodes(memories)
        todo_category_to_nodes = build_todo_category_to_nodes(memories)

        # Build timeline data
        node_timestamps, min_date, max_date = _build_timeline_data(memories)
        latest_memory = _build_latest_memory(memories)

        # Build cluster data using Louvain community detection
        cluster_data = _build_cluster_data(conn, memories)
        ssot_state = _build_ssot_cluster_state(memories)
        causal_state = _build_causal_state(memories, ssot_state["nodePrimaryCluster"], tag_to_nodes)

        # Apply deterministic layout + causal/session metadata into node payload.
        coords = causal_state.get("layoutMeta", {}).get("coords", {})
        node_causal_leaf = causal_state.get("nodeCausalLeaf", {})
        node_causal_path = causal_state.get("nodeCausalPath", {})
        node_session_bucket = causal_state.get("nodeSessionBucket", {})
        node_section = causal_state.get("nodeSection", {})
        for node in nodes:
            key = str(node["id"])
            if key in coords:
                node["x"] = coords[key]["x"]
                node["y"] = coords[key]["y"]
            node["causalCode"] = node_causal_leaf.get(key, "9.9")
            node["causalPath"] = node_causal_path.get(key, [])
            node["sessionBucket"] = node_session_bucket.get(key, "unknown-session")
            node["section"] = node_section.get(key, "uncategorized")

        result = {
            "nodes": nodes,
            "edges": edges,
            "tagColors": tag_colors,
            "tagToNodes": tag_to_nodes,
            "nodeTags": node_tags,
            "sectionToNodes": section_to_nodes,
            "subsectionToNodes": path_to_nodes,
            "sessionToNodes": session_to_nodes,
            "statusToNodes": status_to_nodes,
            "issueCategoryToNodes": issue_category_to_nodes,
            "todoStatusToNodes": todo_status_to_nodes,
            "todoCategoryToNodes": todo_category_to_nodes,
            "duplicateIds": list(duplicate_ids),
            "nodeTimestamps": node_timestamps,
            "minDate": min_date,
            "maxDate": max_date,
            "latestMemory": latest_memory,
        }
        result.update(cluster_data)
        result.update(ssot_state)
        result.update(causal_state)
        return result

    finally:
        conn.close()


def get_memory_for_api(memory_id: int) -> Dict[str, Any]:
    """Get a single memory with expanded R2 URLs for API response."""
    conn = connect()
    try:
        m = get_memory(conn, memory_id)
        if not m:
            return {"error": "not_found"}

        meta = _expand_r2_urls(m.get("metadata"))

        return {
            "id": m["id"],
            "content": m["content"],
            "tags": m.get("tags", []),
            "created": m.get("created_at", ""),
            "updated": m.get("updated_at"),
            "metadata": meta,
        }
    finally:
        conn.close()


def export_graph_html(
    output_path: Optional[str] = None, min_score: float = 0.40
) -> Dict[str, Any]:
    """Generate static HTML knowledge graph visualization.

    Args:
        output_path: Path to save HTML file, or None to return HTML in result.
        min_score: Minimum similarity score for edges.

    Returns:
        Dict with node/edge counts, tags, and optionally path or html.
    """
    conn = connect()
    try:
        memories = list_memories(conn, None, None, None, 0, None, None, None, None, None)
        if not memories:
            return {"error": "no_memories", "message": "No memories to visualize"}

        rebuild_crossrefs(conn)

        # Build edges first to calculate connection counts for node sizing
        edges = _build_edges(conn, memories, min_score)
        connection_counts = _count_connections(edges)

        # Find duplicates (similarity >= 0.7)
        duplicate_ids = _find_duplicate_ids(conn, memories)

        tag_colors = _build_tag_colors(memories)
        nodes = _build_nodes(memories, tag_colors, connection_counts, duplicate_ids)
        tag_to_nodes = _build_tag_to_nodes(memories)
        section_to_nodes, path_to_nodes = _build_section_mappings(memories)
        status_to_nodes = build_status_to_nodes(memories)
        issue_category_to_nodes = build_issue_category_to_nodes(memories)
        todo_status_to_nodes = build_todo_status_to_nodes(memories)
        todo_category_to_nodes = build_todo_category_to_nodes(memories)

        # Build timeline data
        node_timestamps, min_date, max_date = _build_timeline_data(memories)

        # Build memories data for inline display
        memories_data = {}
        for m in memories:
            meta = _expand_r2_urls(m.get("metadata"))
            memories_data[m["id"]] = {
                "id": m["id"],
                "tags": m.get("tags", []),
                "created": m.get("created_at", ""),
                "updated": m.get("updated_at"),
                "content": m["content"],
                "metadata": meta,
            }

        # Build cluster data using Louvain community detection
        cluster_data = _build_cluster_data(conn, memories)

        # Build HTML components
        legend_html = _build_legend_html(tag_colors)
        sections_html = _build_sections_html(section_to_nodes, path_to_nodes)
        issues_legend_html = build_issue_legend_html(status_to_nodes, issue_category_to_nodes)
        todos_legend_html = build_todo_legend_html(todo_status_to_nodes, todo_category_to_nodes)
        html = build_static_html(
            nodes_json=json.dumps(nodes),
            edges_json=json.dumps(edges),
            memories_json=json.dumps(memories_data),
            tag_to_nodes_json=json.dumps(tag_to_nodes),
            section_to_nodes_json=json.dumps(section_to_nodes),
            path_to_nodes_json=json.dumps(path_to_nodes),
            status_to_nodes_json=json.dumps(status_to_nodes),
            issue_category_to_nodes_json=json.dumps(issue_category_to_nodes),
            todo_status_to_nodes_json=json.dumps(todo_status_to_nodes),
            todo_category_to_nodes_json=json.dumps(todo_category_to_nodes),
            legend_html=legend_html,
            sections_html=sections_html,
            issues_legend_html=issues_legend_html,
            todos_legend_html=todos_legend_html,
            duplicate_ids_json=json.dumps(list(duplicate_ids)),
            node_timestamps_json=json.dumps(node_timestamps),
            min_date=min_date,
            max_date=max_date,
            version=_get_memora_version(),
            cluster_to_nodes_json=json.dumps(cluster_data["clusterToNodes"]),
            cluster_colors_json=json.dumps(cluster_data["clusterColors"]),
            cluster_meta_json=json.dumps(cluster_data["clusterMeta"]),
        )

        result = {
            "nodes": len(nodes),
            "edges": len(edges),
            "tags": list(tag_colors.keys()),
        }

        if output_path is not None:
            with open(output_path, "w") as f:
                f.write(html)
            result["path"] = output_path
        else:
            result["html"] = html

        return result

    finally:
        conn.close()
