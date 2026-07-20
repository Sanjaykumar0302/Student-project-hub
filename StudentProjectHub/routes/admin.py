from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload

from extensions import db
from models.user import User
from models.project import Project
from models.notification import Notification
from forms import AdminNoteForm, UploadCompletedForm
from services.project_service import update_status
from services.file_service import store_completed_file
from services.dashboard_service import admin_overview, status_breakdown, project_type_breakdown
from utils.decorators import admin_required
from utils.constants import NEXT_STATUS
from models.admin_note import AdminNote

PROJECTS_PER_PAGE = 20
STUDENTS_PER_PAGE = 25

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/dashboard")
@login_required
@admin_required
def dashboard():
    stats = admin_overview()
    recent_projects = (
        Project.query.options(joinedload(Project.student))
        .order_by(Project.created_at.desc())
        .limit(8)
        .all()
    )
    return render_template("admin/dashboard.html", stats=stats, recent_projects=recent_projects)


@admin_bp.route("/students")
@login_required
@admin_required
def students():
    page = request.args.get("page", 1, type=int)
    pagination = (
        User.query.filter_by(role="student")
        .order_by(User.created_at.desc())
        .paginate(page=page, per_page=STUDENTS_PER_PAGE, error_out=False)
    )
    student_ids = [s.id for s in pagination.items]
    project_counts = dict(
        db.session.query(Project.student_id, db.func.count(Project.id))
        .filter(Project.student_id.in_(student_ids))
        .group_by(Project.student_id)
        .all()
    ) if student_ids else {}
    return render_template(
        "admin/students.html", students=pagination.items, pagination=pagination, project_counts=project_counts
    )


@admin_bp.route("/projects")
@login_required
@admin_required
def projects():
    page = request.args.get("page", 1, type=int)
    status_filter = request.args.get("status")
    query = Project.query.options(joinedload(Project.student), joinedload(Project.package))
    if status_filter:
        query = query.filter_by(status=status_filter)
    pagination = query.order_by(Project.created_at.desc()).paginate(
        page=page, per_page=PROJECTS_PER_PAGE, error_out=False
    )
    return render_template(
        "admin/projects.html", projects=pagination.items, pagination=pagination, status_filter=status_filter
    )


@admin_bp.route("/projects/<int:project_id>/status", methods=["POST"])
@login_required
@admin_required
def change_status(project_id):
    project = Project.query.get_or_404(project_id)
    new_status = request.form.get("new_status")

    if new_status not in NEXT_STATUS.get(project.status, []):
        flash(f"Cannot move from {project.status} to {new_status}.", "danger")
        return redirect(url_for("project.details", project_id=project.id))

    update_status(project, new_status)
    flash(f"Project status updated to {new_status}.", "success")
    return redirect(url_for("project.details", project_id=project.id))


@admin_bp.route("/projects/<int:project_id>/upload", methods=["GET", "POST"])
@login_required
@admin_required
def upload_completed(project_id):
    project = Project.query.get_or_404(project_id)
    form = UploadCompletedForm()

    if form.validate_on_submit():
        store_completed_file(form.completed_file.data, project.id)
        flash("Deliverable uploaded.", "success")
        return redirect(url_for("project.details", project_id=project.id))

    return render_template("admin/upload_completed.html", form=form, project=project)


@admin_bp.route("/projects/<int:project_id>/notes", methods=["POST"])
@login_required
@admin_required
def add_note(project_id):
    project = Project.query.get_or_404(project_id)
    form = AdminNoteForm()
    if form.validate_on_submit():
        note = AdminNote(project_id=project.id, admin_id=current_user.id, note=form.note.data)
        db.session.add(note)
        db.session.commit()
        flash("Note added.", "success")
    else:
        flash("Note couldn't be added - it needs at least 2 characters.", "danger")
    return redirect(url_for("project.details", project_id=project.id))


@admin_bp.route("/analytics")
@login_required
@admin_required
def analytics():
    stats = admin_overview()
    by_status = status_breakdown()
    by_type = project_type_breakdown()
    return render_template("admin/analytics.html", stats=stats, by_status=by_status, by_type=by_type)


@admin_bp.route("/notifications")
@login_required
@admin_required
def notifications():
    items = (
        Notification.query.filter_by(user_id=current_user.id)
        .order_by(Notification.created_at.desc())
        .all()
    )
    return render_template("admin/notifications.html", notifications=items)


@admin_bp.route("/settings")
@login_required
@admin_required
def settings():
    from models.package import Package
    packages = Package.query.order_by(Package.price).all()
    return render_template("admin/settings.html", packages=packages)
