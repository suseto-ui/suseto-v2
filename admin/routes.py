from flask import request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime

from . import admin_bp
from .models import db, AdminUser, SystemLog, SystemConfig
from .utils import role_required

from flask import send_from_directory
from .services import UPLOAD_FOLDER

@admin_bp.route('/scans', methods=['GET'])
@login_required
@role_required('admin')
def get_all_scans():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 50, type=int)
    
    pagination = GlobalScan.query.order_by(GlobalScan.timestamp.desc()).paginate(page=page, per_page=limit, error_out=False)
    
    scans = [{
        "id": s.id,
        "timestamp": s.timestamp.isoformat(),
        "scan_type": s.scan_type,
        "raw_data": s.raw_data,
        "parsed_json": s.parsed_json,
        "image_url": f"/admin/scans/image/{s.image_filename}" if s.image_filename else None,
        "ip_address": s.ip_address
    } for s in pagination.items]
    
    return jsonify({"status": "success", "data": scans, "total": pagination.total}), 200

@admin_bp.route('/scans/image/<filename>', methods=['GET'])
@login_required
@role_required('admin')
def get_scan_image(filename):
    # Zabezpečené doručení souboru fotky pouze přihlášenému adminovi
    return send_from_directory(UPLOAD_FOLDER, filename)


@admin_bp.route('/login', methods=['POST'])
def login():
    if current_user.is_authenticated:
        return jsonify({"status": "error", "message": "Již přihlášen"}), 400

    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"status": "error", "message": "Chybí přihlašovací údaje"}), 400

    user = AdminUser.query.filter_by(username=data['username']).first()
    if user and user.check_password(data['password']):
        if not user.is_active:
            return jsonify({"status": "error", "message": "Účet je deaktivován"}), 403
            
        login_user(user)
        user.last_login = datetime.utcnow()
        db.session.commit()
        return jsonify({"status": "success", "message": "Přihlášení úspěšné", "role": user.role}), 200
        
    return jsonify({"status": "error", "message": "Neplatné jméno nebo heslo"}), 401

@admin_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"status": "success", "message": "Odhlášení úspěšné"}), 200

@admin_bp.route('/dashboard/summary', methods=['GET'])
@login_required
@role_required('admin')
def dashboard_summary():
    return jsonify({
        "status": "success",
        "data": {
            "total_users": AdminUser.query.count(),
            "critical_errors": SystemLog.query.filter_by(level='ERROR').count(),
            "system_status": "online"
        }
    }), 200

@admin_bp.route('/logs', methods=['GET'])
@login_required
@role_required('admin')
def get_logs():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('limit', 50, type=int)
    level_filter = request.args.get('level')
    module_filter = request.args.get('module')

    query = SystemLog.query
    if level_filter: query = query.filter_by(level=level_filter.upper())
    if module_filter: query = query.filter_by(module=module_filter)

    pagination = query.order_by(SystemLog.timestamp.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    logs = [{"id": l.id, "timestamp": l.timestamp.isoformat(), "level": l.level, "module": l.module, "message": l.message} for l in pagination.items]
    return jsonify({"status": "success", "data": logs}), 200

@admin_bp.route('/users', methods=['GET', 'POST'])
@login_required
@role_required('superadmin')
def manage_users():
    if request.method == 'GET':
        users = AdminUser.query.all()
        return jsonify({"status": "success", "data": [{
            "id": u.id, "username": u.username, "role": u.role, "is_active": u.is_active, 
            "last_login": u.last_login.isoformat() if u.last_login else None
        } for u in users]}), 200
        
    if request.method == 'POST':
        data = request.get_json()
        if AdminUser.query.filter_by(username=data['username']).first():
            return jsonify({"status": "error", "message": "Uživatel již existuje"}), 409
            
        new_user = AdminUser(username=data['username'], role=data.get('role', 'admin'), is_active=data.get('is_active', True))
        new_user.set_password(data['password'])
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"status": "success", "message": "Uživatel vytvořen"}), 201

@admin_bp.route('/users/<int:user_id>', methods=['PUT', 'DELETE'])
@login_required
@role_required('superadmin')
def manage_single_user(user_id):
    user = AdminUser.query.get_or_404(user_id)
    if user.id == current_user.id:
        return jsonify({"status": "error", "message": "Nelze modifikovat vlastní účet touto cestou"}), 403

    if request.method == 'PUT':
        data = request.get_json()
        if 'role' in data: user.role = data['role']
        if 'is_active' in data: user.is_active = data['is_active']
        if 'password' in data and data['password'].strip(): user.set_password(data['password'])
        db.session.commit()
        return jsonify({"status": "success", "message": "Uživatel upraven"}), 200

    if request.method == 'DELETE':
        db.session.delete(user)
        db.session.commit()
        return jsonify({"status": "success", "message": "Uživatel smazán"}), 200

@admin_bp.route('/settings', methods=['GET', 'PUT'])
@login_required
@role_required('superadmin')
def manage_settings():
    if request.method == 'GET':
        configs = SystemConfig.query.all()
        return jsonify({"status": "success", "data": {cfg.key: {"value": cfg.value, "description": cfg.description} for cfg in configs}}), 200
        
    if request.method == 'PUT':
        data = request.get_json()
        for item in data:
            key, value = item.get('key'), item.get('value')
            if not key or value is None: continue
            
            config = SystemConfig.query.filter_by(key=key).first()
            if config:
                config.value = str(value)
            else:
                db.session.add(SystemConfig(key=key, value=str(value), description=item.get('description', '')))
        db.session.commit()
        return jsonify({"status": "success", "message": "Konfigurace uložena"}), 200
