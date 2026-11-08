"""Opt-in, group-level research event instrumentation for Lab 2a.

No Kafka dependency; research records are stored separately from teaching audit.
"""
from __future__ import annotations

import csv
import json
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

EVENT_TYPES = frozenset({
    "session_started", "case_selected", "evidence_inspected", "xai_inspected",
    "rai_inspected", "meta_ai_inspected", "ai_challenged",
    "additional_evidence_requested", "human_decision", "session_ended",
})
GROUP_RE = re.compile(r"^NG-[0-9]{3,5}$")
DEFAULT_PATH = Path("data/research/interactions.jsonl")


def research_enabled() -> bool:
    return os.getenv("LAB2A_RESEARCH_MODE", "0").strip().lower() in {"1", "true", "yes"}


def validate_group(group_id: str) -> str:
    group_id = group_id.strip().upper()
    if not GROUP_RE.fullmatch(group_id):
        raise ValueError("Group ID must be NG- followed by 3 to 5 digits (e.g., NG-014)")
    return group_id


def new_session_id() -> str:
    return "RS-" + uuid.uuid4().hex[:16]


def log_event(
    *, group_id: str, session_id: str, event_type: str,
    alert_id: str | None = None, scenario_id: str | None = None,
    condition: str = "standard", details: dict[str, Any] | None = None,
    path: str | Path = DEFAULT_PATH,
) -> dict[str, Any] | None:
    """Append a pseudonymous event only when explicitly enabled.

    Do not pass names, emails, student IDs, or free-text justifications to details.
    """
    if not research_enabled():
        return None
    group_id = validate_group(group_id)
    if event_type not in EVENT_TYPES:
        raise ValueError(f"Unsupported research event: {event_type}")
    if not re.fullmatch(r"RS-[0-9a-f]{16}", session_id):
        raise ValueError("Invalid research session ID")
    details = details or {}
    allowed = {"decision", "reason_category", "evidence_count", "decision_latency_seconds", "justification_length", "evidence_reference_count"}
    if set(details) - allowed:
        raise ValueError("Research event details contain non-whitelisted keys")
    record = {
        "schema_version": "1.0", "event_id": uuid.uuid4().hex,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "group_id": group_id, "session_id": session_id,
        "scenario_id": scenario_id, "alert_id": alert_id,
        "condition": condition, "event_type": event_type, "details": details,
    }
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, ensure_ascii=True) + "\n")
    return record


def export_csv(source: str | Path = DEFAULT_PATH, output: str | Path = "exports/research_events.csv") -> int:
    """Flatten event records; preserves event-level (not individual-level) observations."""
    source = Path(source)
    if not source.is_file():
        raise FileNotFoundError(f"No research events found at {source}")
    columns = ["schema_version", "event_id", "timestamp_utc", "group_id", "session_id",
               "scenario_id", "alert_id", "condition", "event_type", "decision",
               "reason_category", "evidence_count", "decision_latency_seconds",
               "justification_length", "evidence_reference_count"]
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with source.open(encoding="utf-8") as reader, output.open("w", newline="", encoding="utf-8") as writer:
        csv_writer = csv.DictWriter(writer, fieldnames=columns)
        csv_writer.writeheader()
        for line in reader:
            if not line.strip():
                continue
            record = json.loads(line)
            row = {key: record.get(key) for key in columns}
            row.update({key: record.get("details", {}).get(key) for key in columns if key in record.get("details", {})})
            csv_writer.writerow(row)
            count += 1
    return count
