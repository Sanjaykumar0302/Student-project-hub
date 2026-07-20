from datetime import datetime
from extensions import db


class UploadedFile(db.Model):
    __tablename__ = "uploaded_files"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False, index=True)

    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(20), nullable=False)  # 'requirement' or 'completed'
    uploaded_by_role = db.Column(db.String(20), nullable=False)  # 'student' or 'admin'
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def relative_path(self):
        # stored_filename holds the full storage key as generated at upload
        # time (works as both an S3 object key and a local-disk relative path).
        return self.stored_filename

    def __repr__(self):
        return f"<UploadedFile {self.original_filename} ({self.file_type})>"
