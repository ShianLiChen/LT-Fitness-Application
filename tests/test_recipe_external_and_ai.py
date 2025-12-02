# -------------------------
# TheMealDB Tests
# -------------------------
def test_search_external_no_query(client, test_user, auth_headers):
    """
    Test searching external API with an empty query.
    Expects an empty list response and status 200.
    """
    headers = auth_headers(test_user.id)
    resp = client.get("/recipes/api/search-external?query=", headers=headers)
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_search_external_success(client, test_user, auth_headers, mocker):
    """
    Test successful search against TheMealDB external API.
    Mocks the API response and verifies the formatted output.
    """
    headers = auth_headers(test_user.id)

    # Fake response from external API
    fake_api_response = {
        "meals": [
            {
                "strMeal": "Test Meal",
                "strMealThumb": "http://image.jpg",
                "strInstructions": "Cook it",
                "strIngredient1": "Chicken",
                "strMeasure1": "1 lb",
                "strIngredient2": "Salt",
                "strMeasure2": "1 tsp",
                "strIngredient3": "",
            }
        ]
    }

    # Mock requests.get to return fake response
    mock_resp = mocker.Mock()
    mock_resp.json.return_value = fake_api_response
    mocker.patch("src.routes.recipe_routes.requests.get", return_value=mock_resp)

    resp = client.get("/recipes/api/search-external?query=chicken", headers=headers)
    data = resp.get_json()

    # Assertions
    assert resp.status_code == 200
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["title"] == "Test Meal"
    assert "Chicken" in data[0]["ingredients"]
    assert data[0]["source"] == "TheMealDB"


def test_search_external_api_failure(client, test_user, auth_headers, mocker):
    """
    Test behavior when TheMealDB API fails.
    Expects a 500 status code and error message.
    """
    headers = auth_headers(test_user.id)

    # Simulate API failure
    mocker.patch("src.routes.recipe_routes.requests.get", side_effect=Exception("API down"))
    resp = client.get("/recipes/api/search-external?query=pasta", headers=headers)
    data = resp.get_json()

    assert resp.status_code == 500
    assert "error" in data


# -------------------------
# Ollama AI Tests
# -------------------------
def test_generate_ai_success(client, test_user, auth_headers, mocker):
    """
    Test generating AI recipe successfully using Ollama API.
    Mocks API response and verifies the returned data.
    """
    headers = auth_headers(test_user.id)

    fake_ollama = {"response": '{"title":"AI Dish","calories":450,"protein":20}'}
    mock_resp = mocker.Mock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = fake_ollama
    mocker.patch("src.routes.recipe_routes.requests.post", return_value=mock_resp)

    resp = client.post("/recipes/api/generate-ai", json={"prompt": "chicken"}, headers=headers)
    data = resp.get_json()

    assert resp.status_code == 200
    assert "AI Dish" in data["response"]


def test_generate_ai_fallback_on_exception(client, test_user, auth_headers, mocker):
    """
    Test AI generation fallback when Ollama API raises an exception.
    Should return 200 with a fallback response.
    """
    headers = auth_headers(test_user.id)

    # Simulate API exception
    mocker.patch("src.routes.recipe_routes.requests.post", side_effect=Exception("Ollama Down"))
    resp = client.post("/recipes/api/generate-ai", json={"prompt": "anything"}, headers=headers)
    data = resp.get_json()

    assert resp.status_code == 200
    assert "Fallback" in data["response"]


def test_generate_ai_bad_status(client, test_user, auth_headers, mocker):
    """
    Test AI generation fallback when Ollama API returns non-200 status.
    Should return 200 with a fallback response.
    """
    headers = auth_headers(test_user.id)

    # Mock API returning 500
    mock_resp = mocker.Mock()
    mock_resp.status_code = 500
    mocker.patch("src.routes.recipe_routes.requests.post", return_value=mock_resp)

    resp = client.post("/recipes/api/generate-ai", json={"prompt": "food"}, headers=headers)
    data = resp.get_json()

    assert resp.status_code == 200
    assert "Fallback" in data["response"]
