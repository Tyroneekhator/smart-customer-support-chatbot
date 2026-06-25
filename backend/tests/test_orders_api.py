def test_admin_can_create_manual_order_with_items(client, auth_headers):
    response = client.post(
        "/api/orders/",
        json={
            "session_id": "manual-session-1",
            "customer_name": "Tyrone",
            "delivery_method": "pickup",
            "items": [
                {"product_name": "Sugar Cookie", "quantity": 2},
                {"product_name": "Macaron Cookie", "quantity": 1},
            ],
        },
        headers=auth_headers,
    )

    assert response.status_code == 201
    order = response.json()
    assert order["session_id"] == "manual-session-1"
    assert order["status"] == "pending"
    assert order["total_price"] == 6.5
    assert len(order["items"]) == 2


def test_admin_can_update_order_status_and_customer_details(client, auth_headers):
    created_order = client.post(
        "/api/orders/",
        json={
            "session_id": "manual-session-2",
            "items": [{"product_name": "Shortbread Cookie", "quantity": 1}],
        },
        headers=auth_headers,
    ).json()
    order_id = created_order["id"]

    customer_response = client.patch(
        f"/api/orders/{order_id}/customer",
        json={"customer_phone": "08000000000", "notes": "No bag needed."},
        headers=auth_headers,
    )
    status_response = client.patch(
        f"/api/orders/{order_id}/status",
        json={"status": "completed"},
        headers=auth_headers,
    )

    assert customer_response.status_code == 200
    assert customer_response.json()["customer_phone"] == "08000000000"
    assert status_response.status_code == 200
    assert status_response.json()["status"] == "completed"


def test_invalid_order_status_is_rejected(client, auth_headers):
    created_order = client.post(
        "/api/orders/",
        json={
            "session_id": "manual-session-3",
            "items": [{"product_name": "Sugar Cookie", "quantity": 1}],
        },
        headers=auth_headers,
    ).json()

    response = client.patch(
        f"/api/orders/{created_order['id']}/status",
        json={"status": "lost"},
        headers=auth_headers,
    )

    assert response.status_code == 400
    assert "Invalid status" in response.json()["detail"]


def test_manual_order_rejects_unavailable_or_missing_product(client, auth_headers):
    response = client.post(
        "/api/orders/",
        json={
            "session_id": "manual-session-4",
            "items": [{"product_name": "Not Real Cookie", "quantity": 1}],
        },
        headers=auth_headers,
    )

    assert response.status_code == 404
    assert "Product not found" in response.json()["detail"]
