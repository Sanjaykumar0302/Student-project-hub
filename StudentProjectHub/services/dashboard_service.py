from sqlalchemy import func
from extensions import db
from models.project import Project
from models.user import User
from models.payment import Payment


def admin_overview():
    total_students = User.query.filter_by(role="student").count()
    total_projects = Project.query.count()
    pending = Project.query.filter_by(status="Pending").count()
    in_progress = Project.query.filter(Project.status.in_(["Accepted", "Working"])).count()
    completed = Project.query.filter(Project.status.in_(["Completed", "Delivered"])).count()

    revenue = (
        db.session.query(func.coalesce(func.sum(Payment.amount), 0))
        .filter(Payment.status == "paid")
        .scalar()
    )

    return {
        "total_students": total_students,
        "total_projects": total_projects,
        "pending": pending,
        "in_progress": in_progress,
        "completed": completed,
        "revenue": revenue,
    }


def status_breakdown():
    rows = (
        db.session.query(Project.status, func.count(Project.id))
        .group_by(Project.status)
        .all()
    )
    return {status: count for status, count in rows}


def project_type_breakdown():
    rows = (
        db.session.query(Project.project_type, func.count(Project.id))
        .group_by(Project.project_type)
        .all()
    )
    return {ptype: count for ptype, count in rows}


def monthly_signups(limit_months=6):
    # Grouped in Python rather than via SQL's strftime()/to_char(), which
    # differ between SQLite (dev) and Postgres (production) - this works
    # identically on both.
    rows = (
        db.session.query(User.created_at)
        .filter(User.role == "student")
        .order_by(User.created_at)
        .all()
    )
    counts = {}
    for (created_at,) in rows:
        key = created_at.strftime("%Y-%m")
        counts[key] = counts.get(key, 0) + 1
    return sorted(counts.items())[-limit_months:]
