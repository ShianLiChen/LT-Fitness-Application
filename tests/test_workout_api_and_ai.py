# ====================================================
# API NINJAS PROXY (SUCCESS)
# ====================================================
def test_proxy_search_exercises_success(client, test_user, auth_headers, mocker):
    """
    Test that the API Ninjas proxy returns expected exercise data when
    the external API responds successfully.
    """
    headers = auth_headers(test_user.id)

    fake_api_data = [{"name": "Bench Press", "muscle": "chest"}]

    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = fake_api_data

    mocker.patch("src.routes.workout_routes.requests.get", return_value=mock_response)

    resp = client.get(
        "/workouts/api/search-exercises?query=bench",
        headers=headers
    )
    data = resp.get_json()

    assert resp.status_code == 200
    assert data[0]["name"] == "Bench Press"


# ====================================================
# API NINJAS PROXY (FALLBACK MODE)
# ====================================================
def test_proxy_search_exercises_fallback(client, test_user, auth_headers, mocker):
    """
    Test that the API Ninjas proxy returns fallback data when the
    external API fails or raises an exception.
    """
    headers = auth_headers(test_user.id)

    mocker.patch(
        "src.routes.workout_routes.requests.get",
        side_effect=Exception("API Down")
    )

    resp = client.get(
        "/workouts/api/search-exercises?muscle=chest",
        headers=headers
    )
    data = resp.get_json()

    assert resp.status_code == 200
    assert isinstance(data, list)
    assert len(data) > 0


# ====================================================
# OLLAMA AI PROXY (SUCCESS)
# ====================================================
def test_generate_workout_ai_success(client, test_user, auth_headers, mocker):
    """
    Test that the Ollama AI proxy successfully returns AI-generated
    workout data when the external service responds correctly.
    """
    headers = auth_headers(test_user.id)

    fake_ollama = {"response": '[{"exercise_name":"AI Workout"}]'}

    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = fake_ollama

    mocker.patch(
        "src.routes.workout_routes.requests.post",
        return_value=mock_response
    )

    resp = client.post(
        "/workouts/api/generate-workout",
        headers=headers,
        json={"prompt": "leg workout"}
    )
    data = resp.get_json()

    assert resp.status_code == 200
    assert "AI Workout" in data["response"]


# ====================================================
# OLLAMA AI PROXY (FALLBACK MODE)
# ====================================================
def test_generate_workout_ai_fallback(client, test_user, auth_headers, mocker):
    """
    Test that the Ollama AI proxy returns fallback data when the
    AI service fails or raises an exception.
    """
    headers = auth_headers(test_user.id)

    mocker.patch(
        "src.routes.workout_routes.requests.post",
        side_effect=Exception("Ollama Down")
    )

    resp = client.post(
        "/workouts/api/generate-workout",
        headers=headers,
        json={"prompt": "chest workout"}
    )
    data = resp.get_json()

    assert resp.status_code == 200
    assert "AI Generated" in data["response"]
