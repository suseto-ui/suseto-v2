from flask import Blueprint, jsonify, request, render_template
from routes.helpers import current_user, body

core_bp = Blueprint('core', __name__)


@core_bp.get('/health')
def health():
    return jsonify({'status': 'ok', 'mode': 'sandbox-only'})


@core_bp.get('/api/v1/system-status')
def api_system_status():
    return jsonify({'user': current_user()})


@core_bp.post('/api/v1/analyze')
def api_analyze():
    d = body()
    return jsonify({'ok': True, 'payload': d.get('payload') or request.form.get('payload', '')})


@core_bp.route('/label-print/<item_id>')
def label_print(item_id):
    return render_template('pages/label_print.html', item={'id': item_id})
