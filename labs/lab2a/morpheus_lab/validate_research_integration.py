"""Read-only validation of Lab 2a Research Mode integration."""
from __future__ import annotations
import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def validate(root: Path = ROOT) -> dict:
    errors, warnings = [], []
    dashboard = root / 'dashboard.py'
    research = root / 'morpheus_lite' / 'research_mode.py'
    if not dashboard.exists():
        errors.append('dashboard.py is missing; run in the existing Lab 2a directory')
    else:
        source = dashboard.read_text(encoding='utf-8')
        try: ast.parse(source)
        except SyntaxError as exc: errors.append(f'dashboard.py syntax error: {exc}')
        if '# LAB2A_RESEARCH_V1' not in source:
            errors.append('Research Mode integration marker not found in dashboard.py')
        for needle in ['research_track("human_decision"', 'research_track("case_selected"', 'research_track("evidence_inspected"', 'research_track("ai_challenged"']:
            if needle not in source: errors.append(f'Missing integration event: {needle}')
        if 'st.session_state.research_session' not in source:
            errors.append('Research session initialization missing')
    if not research.exists(): errors.append('morpheus_lite/research_mode.py missing')
    else:
        try: ast.parse(research.read_text(encoding='utf-8'))
        except SyntaxError as exc: errors.append(f'research_mode.py syntax error: {exc}')
    if not (root / 'dashboard.research_v1_backup.py').exists():
        warnings.append('No dashboard backup found')
    return {'passed': not errors, 'errors': errors, 'warnings': warnings,
            'checks': {'dashboard_present': dashboard.exists(), 'research_module_present': research.exists()}}

if __name__ == '__main__':
    result = validate(Path(sys.argv[1]) if len(sys.argv)>1 else ROOT)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result['passed'] else 1)
