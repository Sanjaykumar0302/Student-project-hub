from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, logout_user, current_user

from extensions import db
from forms import ProfileEditForm
from services import storage_service

profile_bp = Blueprint("profile", __name__)

AVATAR_EXTENSIONS = {"jpg", "jpeg", "png"}


@profile_bp.route("/")
@login_required
def view():
    if current_user.is_admin:
        return redirect(url_for("admin.settings"))
    return render_template("student/profile.html")


@profile_bp.route("/edit", methods=["GET", "POST"])
@login_required
def edit():
    form = ProfileEditForm(obj=current_user)
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.phone = form.phone.data
        current_user.college = form.college.data

        if form.avatar.data:
            # avatar stores a ready-to-render URL directly (cloud public URL,
            # or a /static/... path in local-disk dev mode) - see storage_service.
            current_user.avatar = storage_service.save_public_file(
                form.avatar.data, f"avatars/user_{current_user.id}", AVATAR_EXTENSIONS
            )

        db.session.commit()
        flash("Profile updated.", "success")
        return redirect(url_for("student.dashboard" if not current_user.is_admin else "admin.dashboard"))

    return render_template("student/edit_profile.html", form=form)


@profile_bp.route("/delete", methods=["POST"])
@login_required
def delete():
    user = current_user
    if user.is_admin:
        flash("Admin accounts cannot be self-deleted.", "danger")
        return redirect(url_for("profile.view"))

    logout_user()
    db.session.delete(user)
    db.session.commit()

    flash("Your account has been deleted successfully.", "info")
    return redirect(url_for("home.index"))
