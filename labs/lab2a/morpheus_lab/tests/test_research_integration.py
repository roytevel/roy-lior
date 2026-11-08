import json
from pathlib import Path
from research_summary import summarize
from validate_research_integration import validate


def test_validator_rejects_missing_dashboard(tmp_path):
    result = validate(tmp_path)
    assert not result['passed']
    assert any('dashboard.py is missing' in x for x in result['errors'])


def test_group_summary(tmp_path):
    src = tmp_path/'events.jsonl'; out = tmp_path/'summary.csv'
    events = [
        {'group_id':'NG-014','session_id':'RS-abc','condition':'standard','event_type':'case_selected'},
        {'group_id':'NG-014','session_id':'RS-abc','condition':'standard','event_type':'ai_challenged'},
        {'group_id':'NG-014','session_id':'RS-abc','condition':'standard','event_type':'human_decision','details':{'decision':'escalate'}}]
    src.write_text(''.join(json.dumps(x)+'\n' for x in events),encoding='utf-8')
    assert summarize(src,out)==1
    s=out.read_text(encoding='utf-8')
    assert 'NG-014' in s and 'escalate' in s
