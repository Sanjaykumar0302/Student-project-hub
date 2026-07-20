from flask import Blueprint, request, redirect, url_for, flash
from flask_login import login_required

from extensions import db
from models.package import Package
from utils.decorators import admin_required

package_bp = Blueprint("package", __name__)


@package_bp.route("/create", methods=["POST"])
@login_required
@admin_required
def create():
    pkg = Package(
        name=request.form["name"],
        price=int(request.form["price"]),
        description=request.form.get("description", ""),
        features=request.form.get("features", ""),
    )
    db.session.add(pkg)
    db.session.commit()
    flash(f"Package '{pkg.name}' created.", "success")
    return redirect(url_for("admin.settings"))


@package_bp.route("/<int:package_id>/update", methods=["POST"])
@login_required
@admin_required
def update(package_id):
    pkg = Package.query.get_or_404(package_id)
    pkg.name = request.form["name"]
    pkg.price = int(request.form["price"])
    pkg.description = request.form.get("description", "")
    pkg.features = request.form.get("features", "")
    db.session.commit()
    flash(f"Package '{pkg.name}' updated.", "success")
    return redirect(url_for("admin.settings"))


@package_bp.route("/<int:package_id>/toggle", methods=["POST"])
@login_required
@admin_required
def toggle(package_id):
    pkg = Package.query.get_or_404(package_id)
    pkg.is_active = not pkg.is_active
    db.session.commit()
    flash(f"Package '{pkg.name}' is now {'active' if pkg.is_active else 'hidden'}.", "info")
    return redirect(url_for("admin.settings"))
