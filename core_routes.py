# routes/core_routes.py
from flask import Blueprint, jsonify, request, Response, render_template, session
from routes.helpers import current_user, require_role, body
from services.config import CONFIG
from services.decision_engine import analyze_payload
from services.generator_engine import profile_bundle
from services.state_machine import build_state_graph, replay_path, get_state_detail
from services.heuristic_engine import build_frontier
from services.auth_lab import simulate
from services.run_store import save_run, list_runs, get_run
from services.transform_service import analyze as transform_analyze, time_formats
from services.registry_store import items
from services.location_service import list_locations
from services.timeline_service import list_for as timeline_list
from services.audit_service import list_entries as audit_list
from services.operations_service import backup, restore
from services.audit_service import write as audit_write

core_bp = Blueprint('core', __name__)

@core_bp.get('/health')
def health():
    return jsonify({'status':'ok','modules':['navigator','generator','state_lab','auth_lab','run_history','aidc_studio','aidc_batch','registry','label_profiles','scanner_lab','transform_lab','dashboard','inventory','insight_lab','label_designer','backup_center'],'mode':'sandbox-only'})

@core_bp.get('/api/v1/system-status')
def api_system_status():
    from pathlib import Path
    data_dir = Path(__file__).resolve().parents[1] / 'data'
    return jsonify({'user': current_user(), 'files': [p.name for p in data_dir.glob('*')] if data_dir.exists() else [], 'locations': len(list_locations()), 'timeline_entries': len(timeline_list()), 'audit_entries': len(audit_list())})

@core_bp.post('/api/v1/expected-audit')
def api_expected_audit():
    rows = body().get('expected', [])
    scanned = body().get('scanned', [])
    exp = {str(x).strip() for x in rows if str(x).strip()}
    sc = {str(x).strip() for x in scanned if str(x).strip()}
    return jsonify({'found': sorted(exp & sc), 'missing': sorted(exp - sc), 'unexpected': sorted(sc - exp)})

@core_bp.post('/api/v1/transform/analyze')
def transform_api():
    d = body()
    return jsonify(transform_analyze(d.get('payload', ''), d.get('key', '')))

@core_bp.get('/api/v1/transform/time')
def transform_time():
    return jsonify(time_formats())

@core_bp.route('/label-print/<item_id>')
def label_print(item_id):
    found = next((x for x in items() if x['id'] == item_id), None)
    if not found:
        return 'Not found', 404
    return render_template('pages/label_print.html', item=found)

@core_bp.post('/api/v1/analyze')
def api_analyze():
    d = body()
    return jsonify(analyze_payload(d.get('payload') or request.form.get('payload', '')))

@core_bp.post('/api/v1/generate-profile')
def api_generate_profile():
    d = body()
    return jsonify(profile_bundle(d.get('seed') or 'sample-seed'))

@core_bp.post('/api/v1/state-graph')
def api_state_graph():
    return jsonify(build_state_graph(body().get('seed') or 'demo'))

@core_bp.post('/api/v1/state-detail')
def api_state_detail():
    return jsonify(get_state_detail(body().get('state_id', 'root')))

@core_bp.post('/api/v1/replay')
def api_replay():
    return jsonify(replay_path(body().get('path') or ['root', 'profile', 'filter', 'validate']))

@core_bp.post('/api/v1/heuristic-run')
def heuristic_run():
    d = body()
    result = build_frontier(d.get('seed', 'demo'), d.get('strategy', 'best_first'), d.get('budget', 8), d.get('weights'))
    saved = save_run({'kind': 'heuristic', 'input': {'seed': d.get('seed', 'demo'), 'strategy': result['strategy'], 'budget': result['budget'], 'weights': result['weights']}, 'summary': {'top_score': result['frontier'][0]['score'] if result['frontier'] else 0, 'count': len(result['frontier'])}})
    return jsonify({**result, 'run': saved})

@core_bp.post('/api/v1/auth-simulate')
def auth_simulate():
    d = body()
    result = simulate(d)
    saved = save_run({'kind': 'auth_simulation', 'input': d, 'summary': {'scenario': result['scenario'], 'risk': result['risk'], 'sandbox': True}})
    return jsonify({**result, 'run': saved})

@core_bp.get('/api/v1/runs')
def api_runs():
    return jsonify({'runs': list_runs()})

@core_bp.get('/api/v1/runs/<run_id>')
def api_run(run_id):
    r = get_run(run_id)
    return (jsonify(r), 200) if r else (jsonify({'error':'not_found'}), 404)
