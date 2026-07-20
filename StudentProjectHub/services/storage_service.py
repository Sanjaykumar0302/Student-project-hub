"""
Storage backend abstraction.

Local disk (the original behavior) works fine for development, but most
managed platforms (Render, Railway, Heroku, etc.) wipe the filesystem on
every restart or redeploy - anything saved to disk disappears. This module
transparently switches to S3-compatible object storage (AWS S3, Cloudflare
R2, DigitalOcean Spaces, ...) whenever S3_BUCKET is configured, and falls
back to local disk otherwise. No route or template code needs to know which
backend is active.
"""
import os
import uuid
from flask import current_app
from werkzeug.utils import secure_filename


def using_cloud_storage():
    return bool(current_app.config.get("S3_BUCKET"))


def _s3_client():
    import boto3
    return boto3.client(
        "s3",
        endpoint_url=current_app.config.get("S3_ENDPOINT_URL") or None,
        aws_access_key_id=current_app.config["S3_ACCESS_KEY_ID"],
        aws_secret_access_key=current_app.config["S3_SECRET_ACCESS_KEY"],
        region_name=current_app.config.get("S3_REGION") or "auto",
    )


def allowed_file(filename, allowed_extensions):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


def _build_key(original_filename, key_prefix):
    safe_name = secure_filename(original_filename)
    ext = safe_name.rsplit(".", 1)[1] if "." in safe_name else ""
    unique = uuid.uuid4().hex[:12]
    stored = f"{unique}.{ext}" if ext else unique
    return f"{key_prefix}/{stored}", safe_name


def save_private_file(file_storage, key_prefix, allowed_extensions):
    """
    For access-gated files (project requirement docs, completed deliverables).
    Returns (original_filename, storage_key), or (None, None) if no file was given.
    Raises ValueError if the extension isn't allowed.
    """
    if not file_storage or not file_storage.filename:
        return None, None
    if not allowed_file(file_storage.filename, allowed_extensions):
        raise ValueError("File type not allowed.")

    key, original_filename = _build_key(file_storage.filename, key_prefix)

    if using_cloud_storage():
        _s3_client().upload_fileobj(file_storage, current_app.config["S3_BUCKET"], key)
    else:
        local_path = os.path.join(current_app.config["UPLOAD_ROOT"], key)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        file_storage.save(local_path)

    return original_filename, key


def download_target(storage_key, download_name=None):
    """
    Returns ("redirect", url) when files live in cloud storage (a short-lived
    presigned URL), or ("file", absolute_path) when they live on local disk.
    The route decides what to do with either.
    """
    if using_cloud_storage():
        params = {"Bucket": current_app.config["S3_BUCKET"], "Key": storage_key}
        if download_name:
            params["ResponseContentDisposition"] = f'attachment; filename="{download_name}"'
        url = _s3_client().generate_presigned_url("get_object", Params=params, ExpiresIn=90)
        return "redirect", url
    return "file", os.path.join(current_app.config["UPLOAD_ROOT"], storage_key)


def save_public_file(file_storage, key_prefix, allowed_extensions):
    """
    For public-facing files (profile avatars). Returns a ready-to-render
    display URL string in either backend - store this directly on the model,
    no extra lookups needed to show it later.
    """
    if not file_storage or not file_storage.filename:
        return None
    if not allowed_file(file_storage.filename, allowed_extensions):
        raise ValueError("File type not allowed.")

    key, _ = _build_key(file_storage.filename, key_prefix)

    if using_cloud_storage():
        client = _s3_client()
        client.upload_fileobj(
            file_storage, current_app.config["S3_BUCKET"], key,
            ExtraArgs={"ACL": "public-read"},
        )
        base = current_app.config.get("S3_PUBLIC_BASE_URL")
        if base:
            return f"{base.rstrip('/')}/{key}"
        return client.generate_presigned_url(
            "get_object",
            Params={"Bucket": current_app.config["S3_BUCKET"], "Key": key},
            ExpiresIn=60 * 60 * 24 * 7,
        )

    local_dir = os.path.join(current_app.root_path, "static", "uploads", "profile")
    os.makedirs(local_dir, exist_ok=True)
    filename = key.split("/")[-1]
    file_storage.save(os.path.join(local_dir, filename))
    return f"/static/uploads/profile/{filename}"
