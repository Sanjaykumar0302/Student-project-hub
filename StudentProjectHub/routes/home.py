from flask import Blueprint, render_template, flash, redirect, url_for

from models.package import Package
from forms import ContactForm

home_bp = Blueprint("home", __name__)


@home_bp.route("/")
def index():
    packages = Package.query.filter_by(is_active=True).all()
    return render_template("home/index.html", packages=packages)


@home_bp.route("/services")
def services():
    return render_template("home/services.html")


@home_bp.route("/packages")
def packages():
    packages = Package.query.filter_by(is_active=True).all()
    return render_template("home/packages.html", packages=packages)


@home_bp.route("/about")
def about():
    return render_template("home/about.html")


@home_bp.route("/faq")
def faq():
    return render_template("home/faq.html")


@home_bp.route("/reviews")
def reviews():
    return render_template("home/reviews.html")


@home_bp.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        # No SMTP configured in this MVP - message is just acknowledged.
        # Wire this up to an email service or save-to-DB if you want to track it.
        flash("Thanks for reaching out! We'll get back to you soon.", "success")
        return redirect(url_for("home.contact"))
    return render_template("home/contact.html", form=form)
