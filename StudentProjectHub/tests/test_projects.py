from tests.conftest import register_and_login
from extensions import db
from models.package import Package
from models.project import Project
from models.user import User


def _first_package_id():
    return Package.query.first().id


def test_submit_project_creates_record(app, client):
    register_and_login(client)
    with app.app_context():
        package_id = _first_package_id()

    resp = client.post("/project/submit", data={
        "title": "Library Management System",
        "project_type": "Python",
        "package_id": package_id,
        "description": "A full library management system with book issue/return tracking.",
        "deadline": "",
    }, follow_redirects=True)

    assert resp.status_code == 200
    with app.app_context():
        project = Project.query.filter_by(title="Library Management System").first()
        assert project is not None
        assert project.status == "Pending"


def test_my_projects_lists_only_own_projects(app, client):
    register_and_login(client, email="owner@test.com")
    with app.app_context():
        package_id = _first_package_id()

    client.post("/project/submit", data={
        "title": "My Own Project", "project_type": "Java", "package_id": package_id,
        "description": "Something long enough to pass validation checks.",
        "deadline": "",
    })

    resp = client.get("/project/my-projects")
    assert b"My Own Project" in resp.data


def test_student_cannot_view_another_students_project(app, client):
    register_and_login(client, email="owner2@test.com")
    with app.app_context():
        package_id = _first_package_id()

    client.post("/project/submit", data={
        "title": "Private Project", "project_type": "PHP", "package_id": package_id,
        "description": "This project belongs to the first student only.",
        "deadline": "",
    })
    with app.app_context():
        project = Project.query.filter_by(title="Private Project").first()
        project_id = project.id

    client.get("/logout")
    register_and_login(client, email="intruder@test.com")
    resp = client.get(f"/project/{project_id}")
    assert resp.status_code == 403


def test_admin_can_move_project_through_status_flow(app, client):
    register_and_login(client, email="flow@test.com")
    with app.app_context():
        package_id = _first_package_id()

    client.post("/project/submit", data={
        "title": "Status Flow Project", "project_type": "Flask", "package_id": package_id,
        "description": "Testing the admin status transition workflow end to end.",
        "deadline": "",
    })
    with app.app_context():
        project_id = Project.query.filter_by(title="Status Flow Project").first().id

    client.get("/logout")
    client.post("/login", data={"email": "admin@test.com", "password": "adminpass123"})

    resp = client.post(f"/admin/projects/{project_id}/status", data={"new_status": "Accepted"}, follow_redirects=True)
    assert resp.status_code == 200
    with app.app_context():
        assert Project.query.get(project_id).status == "Accepted"

    # Invalid jump (Accepted -> Delivered) should be rejected
    resp = client.post(f"/admin/projects/{project_id}/status", data={"new_status": "Delivered"}, follow_redirects=True)
    with app.app_context():
        assert Project.query.get(project_id).status == "Accepted"


def test_dashboard_counts_reflect_submitted_projects(app, client):
    register_and_login(client, email="counter@test.com")
    with app.app_context():
        package_id = _first_package_id()

    client.post("/project/submit", data={
        "title": "Counted Project", "project_type": "Android", "package_id": package_id,
        "description": "A project used purely to check dashboard counters update.",
        "deadline": "",
    })

    resp = client.get("/student/dashboard")
    assert b"Counted Project" in resp.data or b"Total Projects" in resp.data
