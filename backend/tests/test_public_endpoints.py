def test_health_and_api_info_are_public(client):
    health_response = client.get("/health")
    info_response = client.get("/api/info")

    assert health_response.status_code == 200
    assert health_response.json()["status"] == "healthy"
    assert info_response.status_code == 200
    assert "Smart Customer Support Chatbot" in info_response.json()["project_name"]


def test_public_product_menu_is_seeded(client):
    response = client.get("/api/products/")

    assert response.status_code == 200
    products = response.json()
    product_names = {product["name"] for product in products}

    assert len(products) >= 8
    assert "Chocolate Chip Cookie" in product_names
    assert "Macaron Cookie" in product_names


def test_public_product_search_finds_product_by_partial_name(client):
    response = client.get("/api/products/search/chocolate")

    assert response.status_code == 200
    assert response.json()["name"] == "Chocolate Chip Cookie"
