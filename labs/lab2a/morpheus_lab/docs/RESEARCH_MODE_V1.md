# Lab 2a Research Mode v1

## Scope
An optional, group-level, event-based research layer. It does not modify the SOC detector, agent orchestrator, Kafka topics, or existing audit export. No student names are collected in research events. It does not measure individual students.

## Installation
Copy this package's `install_research_mode.py`, `morpheus_lite/research_mode.py`, `export_research_interactions.py`, and `tests/test_research_mode.py` into the existing Lab 2a directory, preserving subdirectories. From that directory:

```powershell
python install_research_mode.py
python -m pytest tests/test_research_mode.py -q
```

The installer backs up `dashboard.py` to `dashboard.research_v1_backup.py` and checks exact source anchors before editing. Do not run it against an unrelated dashboard version.

## Classroom launch

Research disabled (normal teaching):
```powershell
$env:LAB2A_RESEARCH_MODE="0"
python -m streamlit run dashboard.py
```

Research enabled (only after approval and opt-in):
```powershell
$env:LAB2A_RESEARCH_MODE="1"
python -m streamlit run dashboard.py
```

In the sidebar, enter a group number such as `NG-014`, choose the condition and confirm the group has opted in. Start the research session. Use the research-action buttons to record *actual* evidence inspection and challenge events. The existing decision form remains unchanged. End the research session at the end.

## Output
- `data/research/interactions.jsonl`: append-only research events
- `python export_research_interactions.py` -> `exports/research_events.csv`
- Existing `data/audit.jsonl` and `python export_research_data.py` remain available separately.
- Join datasets by `alert_id` (and by scenario/session IDs once those are propagated across the SOC pipeline).

## Limitations and research safeguards
- **Research consent**: the sidebar acknowledgement is an operator confirmation, not a substitute for informed consent, HIT ethics approval/determination, or a separate consent record.
- **Group-level only**: `NG-xxx` may be linkable to student identities via course rosters. Treat as pseudonymous, not anonymous; restrict access and retention.
- **No automatic observation**: the research buttons record self-reported inspections, not independently verified attention. A stronger study should instrument specific expandable evidence panels and interaction transitions.
- **Latency**: v1 measures seconds from research session start to decision, *not* per-alert deliberation time. Do not label this "decision time" without qualification.
- **Condition label only**: selecting `meta_ai_scaffolded` does not hide or reveal Meta-AI guidance. Controlled experiments require an actual UI condition switch and counterbalanced scenarios.
- **No experimental ground truth**: add scenario IDs, difficulty, expected evidence and independent grading rubrics before calculating decision accuracy.
- **Audit safety**: the existing SOC audit still stores free-text justifications; it may contain personal information typed by students. Protect and review separately.
- **Persistence**: research events persist; Streamlit's current UI session state is not restored on restart. Do not assume continuity across restarts.
- **Concurrency**: JSONL appends are not protected by a multi-process lock; for simultaneous multi-group collection use a server-side database or per-session files.
- **Testing**: run integration smoke tests with the actual Kafka/Redpanda stack and dashboard before student deployment.

## Integration validation and group-level summary
After installation, run:

```powershell
python validate_research_integration.py
python -m pytest tests/test_research_mode.py tests/test_research_integration.py -q
```

After a consented pilot, export event records and descriptive group-session counts:

```powershell
python export_research_interactions.py
python research_summary.py
```

The summary file is `exports/research_group_summary.csv`. Its inspection and challenge counts are *self-reported button presses*, not independently observed cognitive actions. It does not compute decision accuracy or a validated Meta-AI skills score.

## Required live smoke test (not automated here)
1. Start Docker Desktop, then `docker compose up -d redpanda redpanda-console`.
2. Start telemetry generator, detector, and orchestrator in separate terminals.
3. Launch Streamlit with `LAB2A_RESEARCH_MODE=0`; confirm the ordinary decision workflow is unchanged and no research events are written.
4. Enable research mode for an authorized test session, enter a test group number, open an alert, record inspection and challenge actions, and submit a decision.
5. End the session; verify that the research JSONL contains the events and the teaching audit JSONL contains the decision.
6. Export CSV and check counts and linkage. Use synthetic test identifiers, not actual student data.
