from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload, selectinload

from models.project import Project
from models.notification import Notification
from services.project_service import dashboard_counts_for_student
from utils.decorators import student_required

student_bp = Blueprint("student", __name__)


@student_bp.route("/dashboard")
@login_required
@student_required
def dashboard():
    counts = dashboard_counts_for_student(current_user.id)
    recent_projects = (
        Project.query.options(joinedload(Project.package))
        .filter_by(student_id=current_user.id)
        .order_by(Project.created_at.desc())
        .limit(5)
        .all()
    )
    return render_template("student/dashboard.html", counts=counts, recent_projects=recent_projects)


@student_bp.route("/notifications")
@login_required
@student_required
def notifications():
    items = (
        Notification.query.filter_by(user_id=current_user.id)
        .order_by(Notification.created_at.desc())
        .all()
    )
    return render_template("student/notifications.html", notifications=items)


@student_bp.route("/downloads")
@login_required
@student_required
def downloads():
    projects = (
        Project.query.options(joinedload(Project.package), selectinload(Project.files))
        .filter_by(student_id=current_user.id)
        .filter(Project.status.in_(["Completed", "Delivered"]))
        .order_by(Project.updated_at.desc())
        .all()
    )
    return render_template("student/downloads.html", projects=projects)
