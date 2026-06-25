def test_dashboard_counts_confirmed_revenue_and_popular_products(client, auth_headers):
    chat_response = client.post(
        "/api/chat/",
        json={"message": "I want 2 chocolate chip"},
    )
    session_id = chat_response.json()["session_id"]
    client.post(
        "/api/chat/",
        json={"message": "confirm", "session_id": session_id},
    )

    dashboard_response = client.get("/api/dashboard/summary", headers=auth_headers)

    assert dashboard_response.status_code == 200
    dashboard = dashboard_response.json()
    assert dashboard["total_orders"] == 1
    assert dashboard["confirmed_orders"] == 1
    assert dashboard["total_revenue"] == 4.0
    assert dashboard["popular_products"][0]["product_name"] == "Chocolate Chip Cookie"


def test_admin_can_view_recent_sessions_and_delete_chat_history(client, auth_headers):
    chat_response = client.post(
        "/api/chat/",
        json={"message": "hello"},
    )
    session_id = chat_response.json()["session_id"]

    sessions_response = client.get("/api/chat/sessions/recent", headers=auth_headers)
    history_response = client.get(f"/api/chat/history/{session_id}", headers=auth_headers)

    assert sessions_response.status_code == 200
    assert sessions_response.json()[0]["session_id"] == session_id
    assert history_response.status_code == 200
    assert len(history_response.json()) == 2

    delete_response = client.delete(f"/api/chat/history/{session_id}", headers=auth_headers)
    deleted_history_response = client.get(f"/api/chat/history/{session_id}", headers=auth_headers)

    assert delete_response.status_code == 200
    assert deleted_history_response.status_code == 404
