from datetime import datetime, timedelta

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

from extensions import db
from models.user import User
from forms import RegisterForm, LoginForm, ForgotPasswordForm, ResetPasswordForm

auth_bp = Blueprint("auth", __name__)


def _serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home.index"))

    form = RegisterForm()
    if form.validate_on_submit():
        existing = User.query.filter_by(email=form.email.data.lower()).first()
        if existing:
            flash("An account with that email already exists.", "danger")
            return render_template("auth/register.html", form=form)

        user = User(
            name=form.name.data,
            email=form.email.data.lower(),
            phone=form.phone.data,
            college=form.college.data,
            role="student",
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash("Account created! You can now log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f"Welcome back, {user.name}!", "success")
            next_page = request.args.get("next")
            if user.is_admin:
                return redirect(next_page or url_for("admin.dashboard"))
            return redirect(next_page or url_for("student.dashboard"))
        flash("Invalid email or password.", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("home.index"))


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            token = _serializer().dumps(user.email, salt="password-reset")
            reset_url = url_for("auth.reset_password", token=token, _external=True)
            # No SMTP configured in this MVP - print the link instead of emailing it.
            # Wire up Flask-Mail (or any provider) here to actually send it.
            current_app.logger.info(f"[password reset] link for {user.email}: {reset_url}")
            print(f"[password reset] link for {user.email}: {reset_url}")
        # Always show the same message so we don't leak which emails are registered.
        flash("If that email is registered, a reset link has been generated (check server console in this MVP).", "info")
        return redirect(url_for("auth.login"))
    return render_template("auth/forgot_password.html", form=form)


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    try:
        email = _serializer().loads(token, salt="password-reset", max_age=3600)
    except SignatureExpired:
        flash("That reset link has expired. Please request a new one.", "danger")
        return redirect(url_for("auth.forgot_password"))
    except BadSignature:
        flash("That reset link is invalid.", "danger")
        return redirect(url_for("auth.forgot_password"))

    user = User.query.filter_by(email=email).first()
    if not user:
        flash("Account not found.", "danger")
        return redirect(url_for("auth.forgot_password"))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash("Your password has been reset. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/reset_password.html", form=form)

@auth_bp.cli.command("set-admin")
def set_admin():
    """Command to create or update the admin account."""
    admin_email = "sanjay0302v@gmail.com"  # Set your desired admin email
    admin_password = "Sanjay@0302V"      # Set your desired admin password

    admin = User.query.filter_by(role="admin").first()
    if not admin:
        admin = User.query.filter_by(email=admin_email.lower()).first()

    if not admin:
        admin = User(
            name="Admin",
            email=admin_email.lower(),
            phone="9380088069",
            college="LVD College",
            role="admin"
        )
        db.session.add(admin)
    else:
        admin.email = admin_email.lower()
        admin.role = "admin"

    admin.set_password(admin_password)
    db.session.commit()
    print(f"Admin updated successfully! Email: {admin.email}")
