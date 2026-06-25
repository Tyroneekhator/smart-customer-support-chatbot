def test_chatbot_creates_multi_item_pending_order(client, auth_headers):
    chat_response = client.post(
        "/api/chat/",
        json={"message": "I want 2 chocolate chip and 1 macaron"},
    )

    assert chat_response.status_code == 200
    chat_data = chat_response.json()
    assert chat_data["intent"] == "order"
    assert "£6.50" in chat_data["reply"]

    session_id = chat_data["session_id"]
    orders_response = client.get(
        f"/api/orders/session/{session_id}",
        headers=auth_headers,
    )

    assert orders_response.status_code == 200
    orders = orders_response.json()
    assert len(orders) == 1
    assert orders[0]["status"] == "pending"
    assert orders[0]["total_price"] == 6.5
    assert len(orders[0]["items"]) == 2


def test_chatbot_confirms_pending_order(client, auth_headers):
    first_response = client.post(
        "/api/chat/",
        json={"message": "I want two sugar cookies"},
    )
    session_id = first_response.json()["session_id"]

    confirm_response = client.post(
        "/api/chat/",
        json={"message": "confirm", "session_id": session_id},
    )

    assert confirm_response.status_code == 200
    assert confirm_response.json()["intent"] == "confirm_order"
    assert "confirmed" in confirm_response.json()["reply"].lower()

    orders = client.get(
        f"/api/orders/session/{session_id}",
        headers=auth_headers,
    ).json()
    assert orders[0]["status"] == "confirmed"


def test_chatbot_saves_customer_and_delivery_details(client, auth_headers):
    start_response = client.post(
        "/api/chat/",
        json={"message": "I want 1 gingerbread cookie"},
    )
    session_id = start_response.json()["session_id"]

    details_response = client.post(
        "/api/chat/",
        json={
            "message": "my name is Tyrone and my phone is 08012345678 deliver to 12 Test Street",
            "session_id": session_id,
        },
    )

    assert details_response.status_code == 200
    assert details_response.json()["intent"] == "order_details"

    order = client.get(
        f"/api/orders/session/{session_id}",
        headers=auth_headers,
    ).json()[0]

    assert order["customer_name"] == "Tyrone"
    assert "08012345678" in order["customer_phone"]
    assert order["delivery_method"] == "delivery"
    assert "12 Test Street" in order["delivery_address"]


def test_chatbot_cancels_pending_order(client, auth_headers):
    first_response = client.post(
        "/api/chat/",
        json={"message": "I want 1 biscotti"},
    )
    session_id = first_response.json()["session_id"]

    cancel_response = client.post(
        "/api/chat/",
        json={"message": "cancel", "session_id": session_id},
    )

    assert cancel_response.status_code == 200
    assert cancel_response.json()["intent"] == "cancel_order"

    order = client.get(
        f"/api/orders/session/{session_id}",
        headers=auth_headers,
    ).json()[0]
    assert order["status"] == "cancelled"


def test_generic_cookie_buy_request_shows_menu_without_creating_order(client, auth_headers):
    response = client.post(
        "/api/chat/",
        json={"message": "i want to buy cookies"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "menu"
    assert "menu" in data["reply"].lower()
    assert "what cookies would you like to buy" in data["reply"].lower()
    assert "Chocolate Chip Cookie" in data["reply"]

    orders_response = client.get(
        f"/api/orders/session/{data['session_id']}",
        headers=auth_headers,
    )
    assert orders_response.status_code == 404


def test_order_again_after_confirmation_shows_menu_without_creating_empty_order(client, auth_headers):
    first_response = client.post(
        "/api/chat/",
        json={"message": "I want 2 chocolate chip and 1 macaron"},
    )
    session_id = first_response.json()["session_id"]

    confirm_response = client.post(
        "/api/chat/",
        json={"message": "confirm", "session_id": session_id},
    )
    assert confirm_response.status_code == 200
    assert confirm_response.json()["intent"] == "confirm_order"

    order_again_response = client.post(
        "/api/chat/",
        json={"message": "i would like to order again", "session_id": session_id},
    )

    assert order_again_response.status_code == 200
    data = order_again_response.json()
    assert data["intent"] == "menu"
    assert "yes please, here is the menu" in data["reply"].lower()
    assert "what cookies would you like to order this time" in data["reply"].lower()
    assert "Chocolate Chip Cookie" in data["reply"]

    orders_response = client.get(
        f"/api/orders/session/{session_id}",
        headers=auth_headers,
    )
    assert orders_response.status_code == 200
    orders = orders_response.json()
    assert len(orders) == 1
    assert orders[0]["status"] == "confirmed"


def test_not_interested_message_gets_polite_pause_reply_without_creating_order(client, auth_headers):
    response = client.post(
        "/api/chat/",
        json={"message": "i am not intrested in cookies"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "not_interested"
    assert data["reply"] == "Ok, please let me know when you are interested."

    orders_response = client.get(
        f"/api/orders/session/{data['session_id']}",
        headers=auth_headers,
    )
    assert orders_response.status_code == 404


def test_interested_after_not_interested_shows_menu(client, auth_headers):
    first_response = client.post(
        "/api/chat/",
        json={"message": "I am not interested"},
    )
    session_id = first_response.json()["session_id"]

    interested_response = client.post(
        "/api/chat/",
        json={"message": "I am interested", "session_id": session_id},
    )

    assert interested_response.status_code == 200
    data = interested_response.json()
    assert data["intent"] == "menu"
    assert "yes please, here is the menu" in data["reply"].lower()
    assert "what cookies would you like to buy" in data["reply"].lower()
    assert "Chocolate Chip Cookie" in data["reply"]

    orders_response = client.get(
        f"/api/orders/session/{session_id}",
        headers=auth_headers,
    )
    assert orders_response.status_code == 404


def test_like_to_order_cookies_shows_menu_without_creating_order(client, auth_headers):
    response = client.post(
        "/api/chat/",
        json={"message": "please i like to order cookies"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "menu"
    assert "yes please, here is the menu" in data["reply"].lower()
    assert "what cookies would you like to buy" in data["reply"].lower()

    orders_response = client.get(
        f"/api/orders/session/{data['session_id']}",
        headers=auth_headers,
    )
    assert orders_response.status_code == 404
