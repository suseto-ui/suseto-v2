# routes/timeline_routes.py
# Blueprint pro /api/v1/timeline*, /api/v1/locations, /api/v1/dashboard*, /api/v1/backup*

from flask import Blueprint, jsonify, request, Response, session
from routes.helpers import current_user, require_role, body
from services.timeline_service import list_for as timeline_list
from services.location_service import list_locations, add_location
from services.audit_service import write as audit_write, list_entries as audit_list
from services.auth_service import list_users
from services.operations_service import backup, restore
import csv
import io
import datetime
from collections import defaultdict

timeline_bp = Blueprint("timeline", __name__)


@timeline_bp.get("/api/v1/timeline")
def api_timeline():
    if not current_user():
        return jsonify({"error": "Přihlas se."}), 401
    return jsonify({"entries": timeline_list(request.args.get("asset_key"))})


@timeline_bp.get("/api/v1/timeline/export")
def api_timeline_export():
    if not current_user():
        return jsonify({"error": "Přihlas se."}), 401
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(["at", "action", "actor", "asset_key", "detail"])
    for r in timeline_list(None):
        cw.writerow(
            [
                r.get("at"),
                r.get("action"),
                r.get("actor"),
                r.get("asset_key"),
                r.get("detail"),
            ]
        )
    return Response(
        si.getvalue().encode("utf-8-sig"),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=timeline.csv"},
    )


@timeline_bp.get("/api/v1/locations")
def api_locations_list():
    if not current_user():
        return jsonify({"error": "Přihlas se."}), 401
    return jsonify({"locations": list_locations()})


@timeline_bp.post("/api/v1/locations")
def api_locations_add():
    if not require_role("admin", "operator"):
        return jsonify({"error": "Vyžadována role operator nebo admin."}), 403
    res = add_location(
        body().get("name", ""),
        body().get("building", ""),
        body().get("room", ""),
        body().get("shelf", ""),
        body().get("slot", ""),
    )
    audit_write("add_location", session.get("username"), res["name"])
    return jsonify(res), 201


@timeline_bp.get("/api/v1/dashboard")
def dashboard_data():
    from services.registry_store import profiles, items

    all_items = items()
    states = {
        x: sum(1 for i in all_items if i["status"] == x)
        for x in ("active", "reserved", "retired")
    }
    return jsonify(
        {
            "total": len(all_items),
            "states": states,
            "profiles": len(profiles()),
            "recent": sorted(
                all_items, key=lambda x: x.get("updated_at", ""), reverse=True
            )[:8],
        }
    )


@timeline_bp.get("/api/v1/dashboard/stats")
def api_dashboard_stats():
    if not current_user():
        return jsonify({"error": "Přihlas se."}), 401
    users = len(list_users())
    locs = len(list_locations())
    timeline = timeline_list(None)
    audit = audit_list()
    today = datetime.datetime.now(datetime.timezone.utc).date()
    scans_by_date = defaultdict(int)
    for t in timeline:
        if t.get("action") == "scan":
            try:
                d = datetime.datetime.fromisoformat(t["at"]).date()
                if 0 <= (today - d).days < 7:
                    scans_by_date[d.isoformat()] += 1
            except:
                pass
    chart_data = []
    for i in range(6, -1, -1):
        d = (today - datetime.timedelta(days=i)).isoformat()
        chart_data.append({"date": d, "count": scans_by_date.get(d, 0)})
    return jsonify(
        {
            "kpis": {
                "users": users,
                "locations": locs,
                "timeline_events": len(timeline),
                "audit_events": len(audit),
            },
            "chart": chart_data,
            "recent": timeline[:10],
        }
    )


@timeline_bp.get("/api/v1/backup")
def make_backup():
    if not require_role("admin"):
        return jsonify({"error": "Vyžadována role admin."}), 403
    audit_write("backup", session.get("username"), "")
    return Response(
        backup(),
        mimetype="application/zip",
        headers={"Content-Disposition": "attachment; filename=suseto-backup.zip"},
    )


@timeline_bp.post("/api/v1/backup/restore")
def restore_backup():
    if not require_role("admin"):
        return jsonify({"error": "Vyžadována role admin."}), 403
    f = request.files.get("file")
    if not f:
        return jsonify({"error": "Nahraj záložní ZIP."}), 400
    try:
        res = restore(f.read())
        audit_write("restore_backup", session.get("username"), str(res))
        return jsonify(res)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
