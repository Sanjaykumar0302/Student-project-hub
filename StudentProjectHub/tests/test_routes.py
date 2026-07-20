def test_homepage_loads(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"StudentProjectHub" in resp.data


def test_public_pages_load(client):
    for path in ["/services", "/packages", "/about", "/faq", "/reviews"]:
        resp = client.get(path)
        assert resp.status_code == 200, f"{path} did not return 200"


def test_contact_form_submission(client):
    resp = client.post("/contact", data={
        "name": "Curious Visitor", "email": "visitor@test.com",
        "message": "Just checking how the contact form behaves.",
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Thanks for reaching out" in resp.data


def test_unknown_route_returns_404(client):
    resp = client.get("/this-route-does-not-exist")
    assert resp.status_code == 404
    assert b"404" in resp.data


def test_login_page_loads(client):
    resp = client.get("/login")
    assert resp.status_code == 200
    assert b"Log In" in resp.data or b"Log in" in resp.data


def test_register_page_loads(client):
    resp = client.get("/register")
    assert resp.status_code == 200


def test_forgot_password_flow_does_not_leak_account_existence(client):
    resp_known = client.post("/forgot-password", data={"email": "admin@test.com"}, follow_redirects=True)
    resp_unknown = client.post("/forgot-password", data={"email": "nobody@test.com"}, follow_redirects=True)
    assert resp_known.status_code == 200 and resp_unknown.status_code == 200
    # Same generic message either way - no confirmation of which emails exist
    assert (b"reset link has been generated" in resp_known.data) == (b"reset link has been generated" in resp_unknown.data)
