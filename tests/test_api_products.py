
def test_api_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_api_products_list(client):
    response = client.get("/api/products")
    assert response.status_code == 200

    data = response.get_json()

    assert data["count"] == 4
    assert len(data["data"]) == 4
    assert all(
        p["status"] == 1 for p in data["data"]
    )


def test_api_search(client):
    response = client.get("/api/products?q=alpha")
    assert response.status_code == 200

    data = response.get_json()
    assert data["count"] == 1
    assert data["data"][0]["name"] == "Alpha Phone"


def test_api_category_filter(client):
    response = client.get("/api/products?category=12")
    assert response.status_code == 200

    names = [
        p["name"] for p in response.get_json()["data"]
    ]
    assert names == ["Gamma Laptop"]


def test_api_sort_price(client):
    response = client.get("/api/products?sort=price_asc")
    assert response.status_code == 200

    prices = [
        p["price"] for p in response.get_json()["data"]
    ]
    assert prices == sorted(prices)


def test_api_pagination(client):
    response = client.get(
        "/api/products?page=2&per_page=2"
    )
    assert response.status_code == 200

    data = response.get_json()
    assert data["page"] == 2
    assert data["count"] == 4
    assert len(data["data"]) == 2


def test_api_product_detail(client):
    response = client.get("/api/products/1")
    assert response.status_code == 200
    assert response.get_json()["name"] == "Alpha Phone"


def test_api_hidden_product(client):
    response = client.get("/api/products/5")
    assert response.status_code == 404


def test_api_invalid_product(client):
    response = client.get("/api/products/99999")
    assert response.status_code == 404


def test_api_invalid_pagination(client):
    response = client.get("/api/products?page=-1")
    assert response.status_code == 400


def test_api_invalid_sort(client):
    response = client.get(
        "/api/products?sort=invalid_option"
    )
    assert response.status_code == 400


def test_api_invalid_category(client):
    response = client.get("/api/products?category=abc")
    assert response.status_code == 400
