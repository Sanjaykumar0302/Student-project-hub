from tests.conftest import register_and_login


def test_register_creates_student(client):
    resp = client.post("/register", data={
        "name": "Jane Doe", "email": "jane@test.com", "phone": "9876543210",
        "college": "ABC College", "password": "password123", "confirm_password": "password123",
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Account created" in resp.data or b"log in" in resp.data.lower()


def test_register_duplicate_email_rejected(client):
    data = {
        "name": "Jane Doe", "email": "dupe@test.com", "phone": "",
        "college": "", "password": "password123", "confirm_password": "password123",
    }
    client.post("/register", data=data)
    resp = client.post("/register", data=data, follow_redirects=True)
    assert b"already exists" in resp.data


def test_login_with_correct_credentials(client):
    resp = register_and_login(client)
    assert resp.status_code == 200
    assert b"Welcome back" in resp.data or b"Dashboard" in resp.data


def test_login_with_wrong_password_fails(client):
    client.post("/register", data={
        "name": "Jane Doe", "email": "jane2@test.com", "phone": "",
        "college": "", "password": "correctpass", "confirm_password": "correctpass",
    })
    resp = client.post("/login", data={"email": "jane2@test.com", "password": "wrongpass"}, follow_redirects=True)
    assert b"Invalid email or password" in resp.data


def test_student_dashboard_requires_login(client):
    resp = client.get("/student/dashboard", follow_redirects=True)
    assert b"log in" in resp.data.lower() or b"Log In" in resp.data


def test_student_cannot_access_admin_dashboard(client):
    register_and_login(client)
    resp = client.get("/admin/dashboard")
    assert resp.status_code == 403


def test_admin_login_reaches_admin_dashboard(client):
    resp = client.post("/login", data={"email": "admin@test.com", "password": "adminpass123"}, follow_redirects=True)
    assert b"Admin Dashboard" in resp.data


def test_logout_clears_session(client):
    register_and_login(client)
    client.get("/logout")
    resp = client.get("/student/dashboard", follow_redirects=True)
    assert b"Log In" in resp.data or b"log in" in resp.data.lower()
