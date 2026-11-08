"""Aggregate observed group-level event counts; no inference of learning outcomes."""
from __future__ import annotations
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


def summarize(source='data/research/interactions.jsonl', output='exports/research_group_summary.csv'):
    records = [json.loads(line) for line in Path(source).read_text(encoding='utf-8').splitlines() if line.strip()]
    groups = defaultdict(list)
    for event in records:
        if event.get('group_id') and event.get('session_id'):
            groups[(event['group_id'], event['session_id'])].append(event)
    columns = ['group_id','session_id','condition','events','cases_selected','evidence_inspections_reported','xai_inspections_reported','rai_inspections_reported','meta_ai_inspections_reported','ai_challenges','additional_evidence_requests','decisions','decisions_approve','decisions_reject','decisions_escalate','decisions_request_more_evidence','decisions_defer']
    dest = Path(output); dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=columns); writer.writeheader()
        for (group, session), events in sorted(groups.items()):
            counts = Counter(e.get('event_type') for e in events)
            choices = Counter(e.get('details',{}).get('decision') for e in events if e.get('event_type') == 'human_decision')
            row = {'group_id':group,'session_id':session,'condition':events[0].get('condition',''), 'events':len(events),
                'cases_selected':counts['case_selected'],'evidence_inspections_reported':counts['evidence_inspected'],
                'xai_inspections_reported':counts['xai_inspected'],'rai_inspections_reported':counts['rai_inspected'],
                'meta_ai_inspections_reported':counts['meta_ai_inspected'],'ai_challenges':counts['ai_challenged'],
                'additional_evidence_requests':counts['additional_evidence_requested'],'decisions':counts['human_decision']}
            for choice in ['approve','reject','escalate','request_more_evidence','defer']:
                row['decisions_'+choice]=choices[choice]
            writer.writerow(row)
    return len(groups)

if __name__ == '__main__':
    print(f'Summarized {summarize()} group sessions')
