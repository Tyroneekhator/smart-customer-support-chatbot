def test_admin_can_create_and_update_product(client, auth_headers):
    create_response = client.post(
        "/api/products/",
        json={
            "name": "Peanut Butter Cookie",
            "description": "Nutty cookie.",
            "price": 2.75,
            "available": True,
        },
        headers=auth_headers,
    )
    assert create_response.status_code == 201
    product_id = create_response.json()["id"]

    update_response = client.patch(
        f"/api/products/{product_id}",
        json={"price": 3.0, "available": False},
        headers=auth_headers,
    )

    assert update_response.status_code == 200
    updated_product = update_response.json()
    assert updated_product["price"] == 3.0
    assert updated_product["available"] is False


def test_duplicate_product_name_is_rejected(client, auth_headers):
    payload = {
        "name": "Chocolate Chip Cookie",
        "description": "Duplicate name.",
        "price": 2.0,
        "available": True,
    }

    response = client.post("/api/products/", json=payload, headers=auth_headers)

    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_product_update_requires_at_least_one_field(client, auth_headers):
    product = client.get("/api/products/search/sugar").json()
    response = client.patch(
        f"/api/products/{product['id']}",
        json={},
        headers=auth_headers,
    )

    assert response.status_code == 400
    assert "at least one" in response.json()["detail"]
