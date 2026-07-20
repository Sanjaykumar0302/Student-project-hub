from datetime import datetime
from extensions import db

STATUS_FLOW = ["Pending", "Accepted", "Working", "Completed", "Delivered"]
STATUS_REJECTED = "Rejected"

PROJECT_TYPES = [
    "Python", "Java", "PHP", "React", "Flask",
    "AI", "Machine Learning", "Data Science", "Android",
]


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    package_id = db.Column(db.Integer, db.ForeignKey("packages.id"), nullable=False)

    title = db.Column(db.String(200), nullable=False)
    project_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    deadline = db.Column(db.Date, nullable=True)

    status = db.Column(db.String(20), nullable=False, default="Pending", index=True)
    price = db.Column(db.Integer, nullable=False, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    files = db.relationship("UploadedFile", backref="project", lazy=True, cascade="all, delete-orphan")
    notes = db.relationship("AdminNote", backref="project", lazy=True, cascade="all, delete-orphan")
    payments = db.relationship("Payment", backref="project", lazy=True, cascade="all, delete-orphan")

    def status_badge_class(self):
        return {
            "Pending": "badge-pending",
            "Accepted": "badge-accepted",
            "Working": "badge-working",
            "Completed": "badge-completed",
            "Delivered": "badge-delivered",
            "Rejected": "badge-rejected",
        }.get(self.status, "badge-pending")

    def is_paid(self):
        return any(p.status == "paid" for p in self.payments)

    def __repr__(self):
        return f"<Project {self.id} '{self.title}' [{self.status}]>"
