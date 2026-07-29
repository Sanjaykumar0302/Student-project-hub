"""
Run once to set up the database:

    python seed.py

Safe to re-run - it only creates the admin account and default packages
if they don't already exist.
"""
from app import create_app
from extensions import db
from models.user import User
from models.package import Package

app = create_app()

with app.app_context():
    db.create_all()

    if not Package.query.first():
        db.session.add_all([
            Package(
                name="Basic",
                price=3000,
                description="Just the finished project, ready to submit.",
                features="Complete project ZIP\nBasic setup instructions\n Synopsis\n Viva Questions with Answers",
            ),
            Package(
                name="Premium",
                price=5000,
                description="Everything you need for submission and viva.",
                features=(
                    "Complete source code\n"
                    "Project report (PDF)\n"
                    "Presentation (PPT)\n"
                    "Disseration\n"
                    "Synopsis\n"
                    "CD\n""viva Questions with Answers"
                ),
            ),
        ])
        db.session.commit()
        print("Created default packages: Basic (₹3000), Premium (₹5000)")
    else:
        print("Packages already exist, skipping.")

    admin_email = app.config["ADMIN_EMAIL"]
    if not User.query.filter_by(email=admin_email).first():
        admin = User(
            name=app.config["ADMIN_NAME"],
            email=admin_email,
            role="admin",
        )
        admin.set_password(app.config["ADMIN_PASSWORD"])
        db.session.add(admin)
        db.session.commit()
        print(f"Created admin account: {admin_email} / (password from .env)")
    else:
        print("Admin account already exists, skipping.")

    print("Database ready.")
