from flask import Blueprint, render_template

timeline_bp = Blueprint('timeline', __name__)

@timeline_bp.route("/timeline")
def timeline_page():
    return render_template("pages/timeline.html")