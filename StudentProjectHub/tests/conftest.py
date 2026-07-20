import pytest

from app import create_app
from extensions import db as _db
from models.user import User
from models.package import Package


@pytest.fixture
def app():
    app = create_app("development")
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        WTF_CSRF_ENABLED=False,
    )

    with app.app_context():
        _db.create_all()

        basic = Package(name="Basic", price=499, description="Basic tier", features="ZIP file")
        premium = Package(name="Premium", price=999, description="Premium tier", features="ZIP\nReport\nPPT")
        _db.session.add_all([basic, premium])

        admin = User(name="Admin", email="admin@test.com", role="admin")
        admin.set_password("adminpass123")
        _db.session.add(admin)

        _db.session.commit()

        yield app

        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def register_and_login(client, email="student@test.com", password="studentpass123", name="Test Student"):
    client.post("/register", data={
        "name": name, "email": email, "phone": "", "college": "",
        "password": password, "confirm_password": password,
    })
    return client.post("/login", data={"email": email, "password": password}, follow_redirects=True)
