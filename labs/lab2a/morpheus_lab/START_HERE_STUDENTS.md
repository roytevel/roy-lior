# Lab 2a — Research-enabled student edition

## Important
This is a synthetic cybersecurity learning lab. Research event logging is **optional** and must be enabled only after the instructor confirms institutional approval and informed consent. Course participation does not depend on research participation. Never enter names, student IDs, passwords, or real security logs. Group IDs are pseudonymous, not anonymous.

## Requirements
Windows PowerShell, Python (compatible with requirements.txt), Docker Desktop with Linux containers running. Install Python dependencies in a virtual environment:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest tests/test_research_mode.py tests/test_research_integration.py -q
```

## Start Kafka/Redpanda
```powershell
docker compose up -d redpanda redpanda-console
docker compose ps
```
Console: http://localhost:18080 ; Kafka host port: 19092. These nondefault ports are intentional to avoid conflicting with an existing teaching lab.

## Run the pipeline (separate PowerShell terminals in the project directory)
Start **detector and orchestrator before generator**. In each terminal activate the virtual environment if needed.

Terminal A:
```powershell
$env:MORPHEUS_INFERENCE_PROVIDER='deterministic'
python .\morpheus_lite_detector.py
```
Terminal B:
```powershell
$env:MORPHEUS_INFERENCE_PROVIDER='deterministic'
python .\agent_orchestrator.py
```
Terminal C:
```powershell
python .\telemetry_generator.py
```
Terminal D (normal teaching; no research event collection):
```powershell
$env:LAB2A_RESEARCH_MODE='0'
python -m streamlit run .\dashboard.py --server.port 8501
```
Open http://localhost:8501 . Click **Fetch new cases from Kafka**. The dashboard currently loads at most 100 records per click and may replay old records on later clicks; this is a known limitation, not a student error.

## Optional research mode (only when authorized and opted in)
Stop dashboard and restart terminal D with:
```powershell
$env:LAB2A_RESEARCH_MODE='1'
$env:MORPHEUS_INFERENCE_PROVIDER='deterministic'
python -m streamlit run .\dashboard.py --server.port 8501
```
Use the instructor-assigned pseudonymous `NG-xxx` group ID. Start session, select a case, inspect evidence and XAI/RAI/Meta-AI, record actual actions using research buttons, submit a decision with a justification, then **End research session**. The `standard` and `meta_ai_scaffolded` labels do **not** yet establish two experimentally distinct interfaces.

## Export research events (only when authorized)
```powershell
python .\export_research_interactions.py
python .\research_summary.py
```
Outputs: `exports/research_events.csv` and `exports/research_group_summary.csv`; original event log: `data/research/interactions.jsonl`. Do not upload `data/audit.jsonl` or other raw logs without instructor instructions; they may contain full free-text justifications. Follow the instructor-approved secure collection channel, not public chat.

## Student activity
1. Inspect a synthetic alert and note `alert_id`, risk score and supporting evidence.
2. Compare the AI recommendation with the evidence and XAI explanation.
3. Identify at least one uncertainty or alternative interpretation.
4. Explain the RAI approval requirement and the role of the human reviewer.
5. Record an independently justified decision.
6. Reflect on when the AI should be challenged or additional evidence requested.

See `docs/STUDENT_LABORATORY_GUIDE.md` for conceptual exercises. **Use START_HERE_STUDENTS.md for current launch commands and ports**; some older documentation refers to original ports (9092/8080).
