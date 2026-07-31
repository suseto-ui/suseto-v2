import os
import sys

# Explicitly add both possible home directory paths for Suseto
paths_to_add = [
    "/home/Suseto/.local/lib/python3.13/site-packages",
    "/home/suseto/.local/lib/python3.13/site-packages",
    "/usr/local/lib/python3.13/site-packages"
]
for p in paths_to_add:
    if os.path.exists(p) and p not in sys.path:
        sys.path.insert(0, p)

from flask import Flask, jsonify, render_template, request, session, Response

from services.config import CONFIG
from services.decision_engine import analyze_payload
from services.generator_engine import profile_bundle
from services.state_machine import build_state_graph, replay_path, get_state_detail
from services.heuristic_engine import build_frontier
from services.auth_lab import simulate
from services.run_store import save_run, list_runs, get_run
from services.aidc_service import generate_qr, generate_barcode, scan_analysis
from services.aidc_batch import preview_csv, generate_batch
from services.registry_store import profiles, items, add_profile, add_item, set_status, match, export_csv_text, import_csv_text
from services.transform_service import analyze as transform_analyze, time_formats
from services.operations_service import session_create, session_add, session_list, profile as payload_profile, diff as payload_diff, patterns as payload_patterns, gs1, backup, restore
from services.auth_service import list_users, create_user, set_role, toggle_active, verify, delete_user, reset_password, change_password
from services.audit_service import write as audit_write, list_entries as audit_list
from services.decode_service import chain as decode_chain, pattern_library
from services.location_service import list_locations, add_location
from services.timeline_service import add as timeline_add, list_for as timeline_list
app=Flask(__name__,template_folder="templates",static_folder="static"); app.config["TEMPLATES_AUTO_RELOAD"]=True; app.secret_key=CONFIG["SECRET_KEY"]; application=app
def current_user(): return {"username":session.get("username"),"role":session.get("role")} if session.get("username") else None
def require_role(*roles):
    u=current_user()
    return u and u.get("role") in roles

@app.route("/")
def home(): return render_template("pages/rozcestnik.html")
@app.route("/navigator")
def navigator(): return render_template("pages/navigator.html")
@app.route("/generator")
def generator(): return render_template("pages/generator.html")
@app.route("/legacy-lab")
def legacy_lab(): return render_template("pages/legacy_lab.html")
@app.route("/state-lab")
def state_lab(): return render_template("pages/state_lab.html")
@app.route("/aidc-studio")
def aidc_studio(): return render_template("pages/aidc_studio.html")
@app.route("/login")
def login_page(): return render_template("pages/login.html", admin_username=CONFIG["ADMIN_USERNAME"], admin_password=CONFIG["DEFAULT_ADMIN_PASSWORD"])
@app.route("/admin")
def admin_page(): return render_template("pages/admin.html")
@app.route("/profile")
def profile_page(): return render_template("pages/profile.html")
@app.route("/decode-lab")
def decode_lab(): return render_template("pages/decode_lab.html")
@app.route("/locations")
def locations_page(): return render_template("pages/locations.html")
@app.route("/status")
def status_page(): return render_template("pages/status.html")
@app.route("/expected-audit")
def expected_audit_page(): return render_template("pages/expected_audit.html")
@app.route("/mobile")
def mobile_page(): return render_template("pages/mobile.html")
@app.route("/debug")
def debug_page(): return render_template("pages/debug.html")
@app.route("/edu")
def edu_page(): return render_template("pages/edu.html")
@app.route("/inventory")
def inventory(): return render_template("pages/inventory.html")
@app.route("/insight-lab")
def insight_lab(): return render_template("pages/insight_lab.html")
@app.route("/label-designer")
def label_designer(): return render_template("pages/label_designer.html")
@app.route("/backup-center")
def backup_center(): return render_template("pages/backup_center.html")
@app.route("/transform-lab")
def transform_lab(): return render_template("pages/transform_lab.html")
@app.route("/dashboard")
def dashboard(): return render_template("pages/dashboard.html")
@app.route("/registry")
def registry(): return render_template("pages/registry.html")
@app.route("/label-profiles")
def label_profiles(): return render_template("pages/label_profiles.html")
@app.route("/aidc-batch")
def aidc_batch(): return render_template("pages/aidc_batch.html")
@app.route("/scanner-lab")
def scanner_lab(): return render_template("pages/scanner_lab.html")
@app.route("/auth-lab")
def auth_lab(): return render_template("pages/auth_lab.html")
@app.route("/runs")
def runs(): return render_template("pages/runs.html")
@app.route("/health")
def health(): return jsonify({"status":"ok","modules":["navigator","generator","state_lab","auth_lab","run_history","aidc_studio","aidc_batch","registry","label_profiles","scanner_lab","transform_lab","dashboard","inventory","insight_lab","label_designer","backup_center"],"mode":"sandbox-only"})
def body(): return request.get_json(silent=True) or {}
@app.get("/api/v1/auth/me")
def auth_me(): return jsonify({"user":current_user()})
@app.post("/api/v1/auth/login")
def auth_login():
 u=verify(body().get("username",""), body().get("password",""))
 if not u:return jsonify({"error":"Neplatné přihlášení."}),401
 session["username"]=u["username"]; session["role"]=u["role"]; audit_write("login",u["username"],u["role"]); return jsonify({"user":u})
@app.post("/api/v1/auth/logout")
def auth_logout():
 audit_write("logout",session.get("username","anonymous"),"")
 session.clear(); return jsonify({"ok":True})
@app.get("/api/v1/admin/users")
def admin_users():
 if not require_role("admin"): return jsonify({"error":"Vyžadována role admin."}),403
 return jsonify({"users":list_users()})
@app.post("/api/v1/admin/users")
def admin_user_create():
 if not require_role("admin"): return jsonify({"error":"Vyžadována role admin."}),403
 try:
  res=create_user(body().get("username"),body().get("password"),body().get("role","viewer")); audit_write("create_user",session.get("username"),res["username"]); return jsonify(res),201
 except ValueError as e:return jsonify({"error":str(e)}),400
@app.post("/api/v1/admin/users/role")
def admin_user_role():
 if not require_role("admin"): return jsonify({"error":"Vyžadována role admin."}),403
 try:
  res=set_role(body().get("username"),body().get("role","viewer")); audit_write("set_role",session.get("username"),f"{body().get('username')}->{body().get('role')}"); return jsonify(res)
 except ValueError as e:return jsonify({"error":str(e)}),404
@app.post("/api/v1/admin/users/toggle")
def admin_user_toggle():
 if not require_role("admin"): return jsonify({"error":"Vyžadována role admin."}),403
 try:
  res=toggle_active(body().get("username")); audit_write("toggle_active",session.get("username"),body().get("username")); return jsonify(res)
 except ValueError as e:return jsonify({"error":str(e)}),404
@app.post("/api/v1/auth/change-password")
def auth_change_password():
 if not current_user(): return jsonify({"error":"Přihlas se."}),401
 try:
  res=change_password(session.get("username"),body().get("old_password",""),body().get("new_password","")); audit_write("change_password",session.get("username"),""); return jsonify(res)
 except ValueError as e:return jsonify({"error":str(e)}),400
@app.get("/api/v1/admin/audit")
def admin_audit():
 if not require_role("admin"): return jsonify({"error":"Vyžadována role admin."}),403
 return jsonify({"entries":audit_list()})
@app.post("/api/v1/admin/users/delete")
def admin_user_delete():
 if not require_role("admin"): return jsonify({"error":"Vyžadována role admin."}),403
 try:
  res=delete_user(body().get("username")); audit_write("delete_user",session.get("username"),body().get("username")); return jsonify(res)
 except ValueError as e:return jsonify({"error":str(e)}),400
@app.post("/api/v1/admin/users/reset-password")
def admin_user_reset_password():
 if not require_role("admin"): return jsonify({"error":"Vyžadována role admin."}),403
 try:
  res=reset_password(body().get("username"),body().get("new_password","")); audit_write("reset_password",session.get("username"),body().get("username")); return jsonify(res)
 except ValueError as e:return jsonify({"error":str(e)}),400
@app.post("/api/v1/decode/chain")
def api_decode_chain():
 if not current_user(): return jsonify({"error":"Přihlas se."}),401
 return jsonify(decode_chain(body().get("payload","")))
@app.post("/api/v1/decode/library")
def api_decode_library():
 if not current_user(): return jsonify({"error":"Přihlas se."}),401
 return jsonify(pattern_library(body().get("payloads",[])))
@app.get("/api/v1/locations")
def api_locations_list():
 if not current_user(): return jsonify({"error":"Přihlas se."}),401
 return jsonify({"locations":list_locations()})
@app.post("/api/v1/locations")
def api_locations_add():
 if not require_role("admin","operator"): return jsonify({"error":"Vyžadována role operator nebo admin."}),403
 res=add_location(body().get("name",""),body().get("building",""),body().get("room",""),body().get("shelf",""),body().get("slot","")); audit_write("add_location",session.get("username"),res["name"]); return jsonify(res),201
@app.get("/api/v1/timeline")
def api_timeline():
 if not current_user(): return jsonify({"error":"Přihlas se."}),401
 return jsonify({"entries":timeline_list(request.args.get("asset_key"))})
@app.get("/api/v1/system-status")
def api_system_status():
 from pathlib import Path
 data_dir=Path(app.root_path)/'data'
 return jsonify({"user":current_user(),"files":[p.name for p in data_dir.glob('*')] if data_dir.exists() else [],"locations":len(list_locations()),"timeline_entries":len(timeline_list()),"audit_entries":len(audit_list())})
@app.post("/api/v1/expected-audit")
def api_expected_audit():
 rows=body().get("expected",[]); scanned=body().get("scanned",[])
 exp={str(x).strip() for x in rows if str(x).strip()}; sc={str(x).strip() for x in scanned if str(x).strip()}
 return jsonify({"found":sorted(exp & sc),"missing":sorted(exp - sc),"unexpected":sorted(sc - exp)})
@app.post("/api/v1/debug/install_pip")
def api_debug_install_pip():
    import subprocess, sys
    try:
        # Install packages using the exact python executable running the web app
        result = subprocess.run(
            ["python3", "-m", "pip", "install", "--user", "qrcode[pil]", "python-barcode[images]", "Pillow"],
            capture_output=True,
            text=True
        )
        output = result.stdout + "\n" + result.stderr

        # Try to dynamically reload the site-packages if possible
        import site
        from pathlib import Path
        user_site = Path.home() / '.local' / 'lib' / f'python{sys.version_info.major}.{sys.version_info.minor}' / 'site-packages'
        if user_site.exists():
            site.addsitedir(str(user_site))

        return jsonify({"ok": True, "log": output})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


@app.get("/api/v1/dashboard/stats")
def api_dashboard_stats():
    if not current_user(): return jsonify({"error":"Přihlas se."}),401
    users = len(list_users())
    locs = len(list_locations())
    timeline = timeline_list(None)
    audit = audit_list()

    import datetime
    from collections import defaultdict
    today = datetime.datetime.now(datetime.timezone.utc).date()
    scans_by_date = defaultdict(int)
    for t in timeline:
        if t.get('action') == 'scan':
            try:
                d = datetime.datetime.fromisoformat(t['at']).date()
                days_ago = (today - d).days
                if 0 <= days_ago < 7:
                    scans_by_date[d.isoformat()] += 1
            except: pass

    chart_data = []
    for i in range(6, -1, -1):
        d = (today - datetime.timedelta(days=i)).isoformat()
        chart_data.append({"date": d, "count": scans_by_date.get(d, 0)})

    return jsonify({
        "kpis": {"users": users, "locations": locs, "timeline_events": len(timeline), "audit_events": len(audit)},
        "chart": chart_data,
        "recent": timeline[:10]
    })

@app.get("/api/v1/timeline/export")
def api_timeline_export():
    if not current_user(): return jsonify({"error":"Přihlas se."}),401
    import csv, io
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['at', 'action', 'actor', 'asset_key', 'detail'])
    for r in timeline_list(None): cw.writerow([r.get('at'), r.get('action'), r.get('actor'), r.get('asset_key'), r.get('detail')])
    return Response(si.getvalue().encode('utf-8-sig'), mimetype='text/csv', headers={'Content-Disposition': 'attachment; filename=timeline.csv'})

@app.get("/api/v1/admin/audit/export")
def api_audit_export():
    if not require_role("admin"): return jsonify({"error":"Vyžadována role admin."}),403
    import csv, io
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['at', 'action', 'actor', 'detail'])
    for r in audit_list(): cw.writerow([r.get('at'), r.get('action'), r.get('actor'), r.get('detail')])
    return Response(si.getvalue().encode('utf-8-sig'), mimetype='text/csv', headers={'Content-Disposition': 'attachment; filename=audit.csv'})

@app.get("/api/v1/debug/env")
def api_debug_env():
    import sys, time
    from pathlib import Path
    import flask
    if not require_role("admin"):
        return jsonify({"error":"Vyžadována role admin."}),403
    res = {"python": sys.version.split(" ")[0], "flask": flask.__version__}

    # 1. Write permission check
    data_dir = Path(app.root_path) / 'data'
    try:
        data_dir.mkdir(exist_ok=True)
        test_file = data_dir / '.write_test'
        test_file.write_text('test')
        test_file.unlink()
        res['data_write'] = "OK"
    except Exception as e:
        res['data_write'] = f"FAIL: {str(e)}"

    # 2. File modification dates (to check deploy success)
    files_to_check = [
        'app.py', 
        'static/js/decode_lab.js', 
        'static/js/menu-delay.js', 
        'static/js/debug.js',
        'templates/pages/decode_lab.html'
    ]
    res['files'] = {}
    for f in files_to_check:
        p = Path(app.root_path) / f
        if p.exists():
            mtime = p.stat().st_mtime
            res['files'][f] = time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(mtime))
        else:
            res['files'][f] = "MISSING"

    # 3. Dependencies check
    deps = {}
    try: 
        import qrcode; deps['qrcode'] = getattr(qrcode, '__version__', 'OK (no __version__)')
    except Exception as e: 
        deps['qrcode'] = f"ERROR: {str(e)}"

    try: 
        import barcode; deps['barcode'] = getattr(barcode, 'version', getattr(barcode, '__version__', 'OK (no version attr)'))
    except Exception as e: 
        deps['barcode'] = f"ERROR: {str(e)}"

    try: 
        import PIL; deps['Pillow'] = PIL.__version__
    except Exception as e: 
        deps['Pillow'] = f"ERROR: {str(e)}"

    res['deps'] = deps
    res['sys_path'] = sys.path

    return jsonify(res)

@app.get("/api/v1/debug/routes")
def api_debug_routes():
 return jsonify({"routes":sorted([str(r.rule) for r in app.url_map.iter_rules()])})
@app.post("/api/v1/debug/ping")
def api_debug_ping():
 return jsonify({"ok":True,"received":body()})
@app.get("/api/v1/inventory/sessions")
def inventory_sessions():
 if not current_user(): return jsonify({"error":"Přihlas se."}),401
 return jsonify({"sessions":session_list()})
@app.post("/api/v1/inventory/sessions")
def inventory_create():
 if not require_role("admin","operator"): return jsonify({"error":"Vyžadována role operator nebo admin."}),403
 res=session_create(body().get("name")); audit_write("create_session",session.get("username"),res["name"]); timeline_add(res["id"],"create_session",session.get("username"),res["name"]); return jsonify(res),201
@app.post("/api/v1/inventory/sessions/<session_id>/scan")
def inventory_scan(session_id):
 if not require_role("admin","operator"): return jsonify({"error":"Vyžadována role operator nebo admin."}),403
 try:
  res=session_add(session_id,body().get("payload","")); audit_write("scan_to_session",session.get("username"),session_id); timeline_add(body().get("payload",""),"scan",session.get("username"),session_id); return jsonify(res)
 except ValueError as e:return jsonify({"error":str(e)}),404
@app.post("/api/v1/insight/profile")
def insight_profile(): return jsonify(payload_profile(body().get("payload","")))
@app.post("/api/v1/insight/diff")
def insight_diff(): return jsonify(payload_diff(body().get("payloads",[])))
@app.post("/api/v1/insight/patterns")
def insight_patterns(): return jsonify({"patterns":payload_patterns(body().get("payloads",[]))})
@app.post("/api/v1/gs1/validate")
def gs1_validate(): return jsonify(gs1(body().get("value","")))
@app.get("/api/v1/backup")
def make_backup():
 if not require_role("admin"): return jsonify({"error":"Vyžadována role admin."}),403
 audit_write("backup",session.get("username"),""); return Response(backup(),mimetype="application/zip",headers={"Content-Disposition":"attachment; filename=suseto-backup.zip"})
@app.post("/api/v1/backup/restore")
def restore_backup():
 if not require_role("admin"): return jsonify({"error":"Vyžadována role admin."}),403
 f=request.files.get("file")
 if not f:return jsonify({"error":"Nahraj záložní ZIP."}),400
 try:
  res=restore(f.read()); audit_write("restore_backup",session.get("username"),str(res)); return jsonify(res)
 except ValueError as e:return jsonify({"error":str(e)}),400
@app.get("/api/v1/dashboard")
def dashboard_data():
 all_items=items(); states={x:sum(1 for i in all_items if i["status"]==x) for x in ("active","reserved","retired")}; return jsonify({"total":len(all_items),"states":states,"profiles":len(profiles()),"recent":sorted(all_items,key=lambda x:x.get("updated_at",""),reverse=True)[:8]})
@app.post("/api/v1/transform/analyze")
def transform_api():
 d=body(); return jsonify(transform_analyze(d.get("payload",""),d.get("key","")))
@app.get("/api/v1/transform/time")
def transform_time(): return jsonify(time_formats())
@app.route("/label-print/<item_id>")
def label_print(item_id):
 found=next((x for x in items() if x["id"]==item_id),None)
 if not found:return "Not found",404
 return render_template("pages/label_print.html",item=found)
@app.get("/api/v1/registry/export")
def registry_export():
 return Response(export_csv_text(),mimetype="text/csv",headers={"Content-Disposition":"attachment; filename=suseto-registry.csv"})
@app.post("/api/v1/registry/import")
def registry_import():
 f=request.files.get("file")
 if not f:return jsonify({"error":"Nahraj CSV soubor."}),400
 try:return jsonify(import_csv_text(f.read()))
 except (ValueError,UnicodeDecodeError) as e:return jsonify({"error":str(e)}),400
@app.get("/api/v1/registry")
def registry_list(): return jsonify({"items":items(request.args.get("q",""),request.args.get("status","")),"profiles":profiles()})
@app.post("/api/v1/registry")
def registry_add():
 try:return jsonify(add_item(body())),201
 except ValueError as e:return jsonify({"error":str(e)}),400
@app.post("/api/v1/registry/<item_id>/status")
def registry_status(item_id):
 try:return jsonify(set_status(item_id,body().get("status")))
 except ValueError as e:return jsonify({"error":str(e)}),400
@app.get("/api/v1/registry/match")
def registry_match(): return jsonify({"item":match(request.args.get("payload",""))})
@app.get("/api/v1/label-profiles")
def profiles_list(): return jsonify({"profiles":profiles()})
@app.post("/api/v1/label-profiles")
def profiles_add():
 try:return jsonify(add_profile(body())),201
 except ValueError as e:return jsonify({"error":str(e)}),400
@app.post("/api/v1/aidc/batch-preview")
def aidc_batch_preview():
 result,status=preview_csv(request.files.get("file")); return jsonify(result),status
@app.post("/api/v1/aidc/batch-generate")
def aidc_batch_generate():
 return generate_batch(request.files.get("file"),request.form.get("column","0"),request.form.get("kind","qr"),request.form.get("format","png"))
@app.post("/api/v1/aidc/generate")
def aidc_generate():
 d=body(); kind=d.get("kind","qr"); fmt=d.get("format","png"); data=d.get("data","")
 return generate_qr(data,fmt) if kind=="qr" else generate_barcode(data,kind,fmt)
@app.post("/api/v1/aidc/analyze-scan")
def aidc_analyze_scan():
 d=body(); result=scan_analysis(d.get("payload","")); result["registry_match"]=match(result["payload"]); saved=save_run({"kind":"aidc_scan","input":{"payload_preview":result["payload"][:120]},"summary":{"classification":result["classification"],"length":result.get("length",0)}}); return jsonify({**result,"run":saved})
@app.post("/api/v1/analyze")
def api_analyze():
 d=body(); return jsonify(analyze_payload(d.get("payload") or request.form.get("payload", "")))
@app.post("/api/v1/generate-profile")
def api_generate_profile():
 d=body(); return jsonify(profile_bundle(d.get("seed") or "sample-seed"))
@app.post("/api/v1/state-graph")
def api_state_graph(): return jsonify(build_state_graph(body().get("seed") or "demo"))
@app.post("/api/v1/state-detail")
def api_state_detail(): return jsonify(get_state_detail(body().get("state_id","root")))
@app.post("/api/v1/replay")
def api_replay(): return jsonify(replay_path(body().get("path") or ["root","profile","filter","validate"]))
@app.post("/api/v1/heuristic-run")
def heuristic_run():
 d=body(); result=build_frontier(d.get("seed","demo"),d.get("strategy","best_first"),d.get("budget",8),d.get("weights")); saved=save_run({"kind":"heuristic","input":{"seed":d.get("seed","demo"),"strategy":result["strategy"],"budget":result["budget"],"weights":result["weights"]},"summary":{"top_score":result["frontier"][0]["score"] if result["frontier"] else 0,"count":len(result["frontier"])}}); return jsonify({**result,"run":saved})
@app.post("/api/v1/auth-simulate")
def auth_simulate():
 d=body(); result=simulate(d); saved=save_run({"kind":"auth_simulation","input":d,"summary":{"scenario":result["scenario"],"risk":result["risk"],"sandbox":True}}); return jsonify({**result,"run":saved})
@app.get("/api/v1/runs")
def api_runs(): return jsonify({"runs":list_runs()})
@app.get("/api/v1/runs/<run_id>")
def api_run(run_id):
 r=get_run(run_id); return (jsonify(r),200) if r else (jsonify({"error":"not_found"}),404)
