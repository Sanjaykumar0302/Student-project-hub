from extensions import db
from models.uploaded_file import UploadedFile
from flask import current_app
from services import storage_service


def store_requirement_file(file_storage, project_id):
    original, key = storage_service.save_private_file(
        file_storage,
        f"requirements/project_{project_id}",
        current_app.config["ALLOWED_EXTENSIONS"],
    )
    if not key:
        return None

    record = UploadedFile(
        project_id=project_id,
        original_filename=original,
        stored_filename=key,
        file_type="requirement",
        uploaded_by_role="student",
    )
    db.session.add(record)
    db.session.commit()
    return record


def store_completed_file(file_storage, project_id):
    original, key = storage_service.save_private_file(
        file_storage,
        f"completed/project_{project_id}",
        current_app.config["ALLOWED_EXTENSIONS"],
    )
    if not key:
        return None

    record = UploadedFile(
        project_id=project_id,
        original_filename=original,
        stored_filename=key,
        file_type="completed",
        uploaded_by_role="admin",
    )
    db.session.add(record)
    db.session.commit()
    return record
