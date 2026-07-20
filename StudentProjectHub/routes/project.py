import razorpay
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, abort, send_file, jsonify
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload

from extensions import db
from models.project import Project
from models.package import Package
from models.payment import Payment
from models.uploaded_file import UploadedFile
from forms import ProjectSubmitForm
from services.project_service import create_project
from services.file_service import store_requirement_file
from services import storage_service
from services.notification_service import notify
from utils.decorators import student_required

project_bp = Blueprint("project", __name__)


def _get_razorpay_client():
    key_id = current_app.config.get("RAZORPAY_KEY_ID")
    key_secret = current_app.config.get("RAZORPAY_KEY_SECRET")
    if not key_id or not key_secret or key_id.endswith("yourkeyid"):
        return None
    return razorpay.Client(auth=(key_id, key_secret))


@project_bp.route("/submit", methods=["GET", "POST"])
@login_required
@student_required
def submit():
    form = ProjectSubmitForm()
    form.package_id.choices = [(p.id, f"{p.name} - ₹{p.price}") for p in Package.query.filter_by(is_active=True).all()]

    if form.validate_on_submit():
        package = Package.query.get_or_404(form.package_id.data)
        project = create_project(current_user.id, package, form)

        if form.requirement_file.data:
            store_requirement_file(form.requirement_file.data, project.id)

        # Notify all admins of a new request
        from models.user import User
        for admin in User.query.filter_by(role="admin").all():
            notify(admin.id, f"New project request: '{project.title}' from {current_user.name}", link=f"/project/{project.id}")

        flash("Your project request has been submitted! We'll review it shortly.", "success")
        return redirect(url_for("project.my_projects"))

    return render_template("student/submit_project.html", form=form)


@project_bp.route("/my-projects")
@login_required
@student_required
def my_projects():
    projects = (
        Project.query.options(joinedload(Project.package))
        .filter_by(student_id=current_user.id)
        .order_by(Project.created_at.desc())
        .all()
    )
    return render_template("student/my_projects.html", projects=projects)


@project_bp.route("/<int:project_id>")
@login_required
def details(project_id):
    project = Project.query.get_or_404(project_id)

    if not current_user.is_admin and project.student_id != current_user.id:
        abort(403)

    razorpay_key = current_app.config.get("RAZORPAY_KEY_ID", "")

    if current_user.is_admin:
        from forms import AdminNoteForm
        return render_template("admin/project_details.html", project=project, note_form=AdminNoteForm())

    return render_template("student/project_details.html", project=project, razorpay_key_id=razorpay_key)


@project_bp.route("/<int:project_id>/checkout", methods=["POST"])
@login_required
@student_required
def checkout(project_id):
    project = Project.query.get_or_404(project_id)
    if project.student_id != current_user.id:
        abort(403)
    if project.status != "Completed":
        flash("Payment unlocks once your project is marked Completed.", "warning")
        return redirect(url_for("project.details", project_id=project.id))
    if project.is_paid():
        flash("This project is already paid for.", "info")
        return redirect(url_for("project.details", project_id=project.id))

    client = _get_razorpay_client()
    amount_paise = project.price * 100

    if client is None:
        # No real Razorpay keys configured - simulate the order so the flow is testable end-to-end.
        payment = Payment(project_id=project.id, amount=project.price, status="created",
                           razorpay_order_id=f"order_simulated_{project.id}")
        db.session.add(payment)
        db.session.commit()
        flash("Razorpay isn't configured yet (using simulated checkout). Add real keys in .env to go live.", "warning")
        return redirect(url_for("project.simulate_payment", project_id=project.id))

    order = client.order.create({
        "amount": amount_paise,
        "currency": "INR",
        "receipt": f"project_{project.id}",
        "payment_capture": 1,
    })
    payment = Payment(project_id=project.id, amount=project.price, status="created",
                       razorpay_order_id=order["id"])
    db.session.add(payment)
    db.session.commit()

    return render_template(
        "student/checkout.html",
        project=project,
        order=order,
        razorpay_key_id=current_app.config["RAZORPAY_KEY_ID"],
    )


@project_bp.route("/<int:project_id>/simulate-payment")
@login_required
@student_required
def simulate_payment(project_id):
    """Dev-only stand-in for the Razorpay checkout UI when no API keys are set."""
    project = Project.query.get_or_404(project_id)
    if project.student_id != current_user.id:
        abort(403)
    return render_template("student/checkout.html", project=project, order=None, razorpay_key_id="")


@project_bp.route("/<int:project_id>/confirm-payment", methods=["POST"])
@login_required
@student_required
def confirm_payment(project_id):
    project = Project.query.get_or_404(project_id)
    if project.student_id != current_user.id:
        abort(403)

    payment = Payment.query.filter_by(project_id=project.id).order_by(Payment.id.desc()).first()
    if not payment:
        return jsonify({"ok": False, "message": "No payment record found."}), 400

    client = _get_razorpay_client()
    if client is not None:
        try:
            client.utility.verify_payment_signature({
                "razorpay_order_id": request.form["razorpay_order_id"],
                "razorpay_payment_id": request.form["razorpay_payment_id"],
                "razorpay_signature": request.form["razorpay_signature"],
            })
        except Exception:
            payment.status = "failed"
            db.session.commit()
            return jsonify({"ok": False, "message": "Signature verification failed."}), 400

        payment.razorpay_payment_id = request.form.get("razorpay_payment_id")
        payment.razorpay_signature = request.form.get("razorpay_signature")

    payment.status = "paid"
    db.session.commit()
    notify(project.student_id, f"Payment received for '{project.title}'. Your files are unlocked!", link=f"/project/{project.id}")

    return jsonify({"ok": True, "redirect": url_for("project.details", project_id=project.id)})


@project_bp.route("/<int:project_id>/download/<int:file_id>")
@login_required
def download_file(project_id, file_id):
    project = Project.query.get_or_404(project_id)
    uploaded = UploadedFile.query.get_or_404(file_id)

    if uploaded.project_id != project.id:
        abort(404)

    if current_user.is_admin:
        pass  # admins can always download
    elif project.student_id != current_user.id:
        abort(403)
    elif uploaded.file_type == "completed" and not project.is_paid():
        flash("Please complete payment to download deliverables.", "warning")
        return redirect(url_for("project.details", project_id=project.id))

    kind, target = storage_service.download_target(uploaded.relative_path(), uploaded.original_filename)
    if kind == "redirect":
        return redirect(target)
    return send_file(target, as_attachment=True, download_name=uploaded.original_filename)
