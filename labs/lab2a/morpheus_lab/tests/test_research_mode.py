import csv
import pytest
from morpheus_lite.research_mode import export_csv, log_event, new_session_id, validate_group


def test_disabled_never_writes(tmp_path, monkeypatch):
    monkeypatch.delenv("LAB2A_RESEARCH_MODE", raising=False)
    path = tmp_path / "events.jsonl"
    assert log_event(group_id="NG-014", session_id=new_session_id(), event_type="case_selected", path=path) is None
    assert not path.exists()


def test_enabled_event_and_export(tmp_path, monkeypatch):
    monkeypatch.setenv("LAB2A_RESEARCH_MODE", "1")
    path = tmp_path / "events.jsonl"
    session = new_session_id()
    event = log_event(group_id="NG-014", session_id=session, event_type="human_decision", alert_id="A1", details={"decision":"escalate", "justification_length":25}, path=path)
    assert event["group_id"] == "NG-014"
    assert "student_name" not in event
    csv_path = tmp_path / "export.csv"
    assert export_csv(path, csv_path) == 1
    with csv_path.open(newline="", encoding="utf-8") as f:
        row = list(csv.DictReader(f))[0]
    assert row["decision"] == "escalate"


def test_reject_personal_data_fields(tmp_path, monkeypatch):
    monkeypatch.setenv("LAB2A_RESEARCH_MODE", "1")
    with pytest.raises(ValueError):
        log_event(group_id="NG-014", session_id=new_session_id(), event_type="case_selected", details={"student_name":"Jane"}, path=tmp_path / "x")


def test_group_validation():
    assert validate_group("ng-014") == "NG-014"
    with pytest.raises(ValueError):
        validate_group("Student 14")
