from extensions import db
from models.project import Project
from utils.constants import NEXT_STATUS
from services.notification_service import notify


def create_project(student_id, package, form):
    project = Project(
        student_id=student_id,
        package_id=package.id,
        title=form.title.data,
        project_type=form.project_type.data,
        description=form.description.data,
        deadline=form.deadline.data,
        price=package.price,
        status="Pending",
    )
    db.session.add(project)
    db.session.commit()
    return project


def can_transition(current_status, new_status):
    return new_status in NEXT_STATUS.get(current_status, [])


def update_status(project, new_status):
    if not can_transition(project.status, new_status):
        raise ValueError(f"Cannot move project from {project.status} to {new_status}")

    project.status = new_status
    db.session.commit()

    messages = {
        "Accepted": f"Your project '{project.title}' has been accepted!",
        "Rejected": f"Your project '{project.title}' was rejected. Check admin notes for details.",
        "Working": f"Work has started on your project '{project.title}'.",
        "Completed": f"Your project '{project.title}' is complete! Payment is required to unlock downloads.",
        "Delivered": f"Your project '{project.title}' has been delivered. Enjoy!",
    }
    if new_status in messages:
        notify(project.student_id, messages[new_status], link=f"/project/{project.id}")

    return project


def dashboard_counts_for_student(student_id):
    rows = (
        db.session.query(Project.status, db.func.count(Project.id))
        .filter(Project.student_id == student_id)
        .group_by(Project.status)
        .all()
    )
    by_status = dict(rows)
    return {
        "total": sum(by_status.values()),
        "pending": by_status.get("Pending", 0),
        "in_progress": by_status.get("Accepted", 0) + by_status.get("Working", 0),
        "completed": by_status.get("Completed", 0) + by_status.get("Delivered", 0),
    }
