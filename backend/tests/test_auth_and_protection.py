def test_admin_can_login_and_read_profile(client, auth_headers):
    profile_response = client.get("/api/auth/me", headers=auth_headers)

    assert profile_response.status_code == 200
    profile = profile_response.json()
    assert profile["username"] == "admin"
    assert profile["is_active"] is True


def test_admin_login_rejects_wrong_password(client):
    response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert "Invalid admin username or password" in response.json()["detail"]


def test_admin_profile_requires_token(client):
    response = client.get("/api/auth/me")

    assert response.status_code == 401
    assert response.json()["detail"] == "Admin login is required."


def test_dashboard_requires_admin_token(client):
    blocked_response = client.get("/api/dashboard/summary")

    assert blocked_response.status_code == 401


def test_admin_endpoints_accept_valid_token(client, auth_headers):
    dashboard_response = client.get("/api/dashboard/summary", headers=auth_headers)
    orders_response = client.get("/api/orders/", headers=auth_headers)

    assert dashboard_response.status_code == 200
    assert orders_response.status_code == 200


def test_product_write_actions_are_protected(client, auth_headers):
    product_payload = {
        "name": "Test Cookie",
        "description": "Created during testing.",
        "price": 3.25,
        "available": True,
    }

    blocked_response = client.post("/api/products/", json=product_payload)
    allowed_response = client.post(
        "/api/products/",
        json=product_payload,
        headers=auth_headers,
    )

    assert blocked_response.status_code == 401
    assert allowed_response.status_code == 201
    assert allowed_response.json()["name"] == "Test Cookie"
