from flask import Blueprint, redirect, url_for, jsonify
from flask_login import login_required, current_user

from services.notification_service import mark_all_read, mark_one_read, unread_count

notification_bp = Blueprint("notification", __name__)


@notification_bp.route("/mark-all-read", methods=["POST"])
@login_required
def mark_all():
    mark_all_read(current_user.id)
    return redirect(url_for("admin.notifications" if current_user.is_admin else "student.notifications"))


@notification_bp.route("/<int:notification_id>/read", methods=["POST"])
@login_required
def mark_one(notification_id):
    n = mark_one_read(notification_id, current_user.id)
    if n and n.link:
        return redirect(n.link)
    return redirect(url_for("admin.notifications" if current_user.is_admin else "student.notifications"))


@notification_bp.route("/unread-count")
@login_required
def unread():
    return jsonify({"count": unread_count(current_user.id)})
