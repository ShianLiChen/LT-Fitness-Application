from models.recipe import Recipe

# -------------------------
# Recipe Save Tests
# -------------------------
def test_save_recipe_missing_fields(client, test_user, auth_headers):
    headers = auth_headers(test_user.id)
    resp = client.post("/recipes/", json={"title": ""}, headers=headers)
    data = resp.get_json()
    assert resp.status_code == 400
    assert data is not None
    assert "errors" in data
    assert "title" in data["errors"]
    assert data["errors"]["title"] == ["Title cannot be empty"]

def test_save_recipe_success(client, test_user, auth_headers):
    headers = auth_headers(test_user.id)
    payload = {"title": "Salad", "ingredients": "Lettuce", "instructions": "Mix"}
    resp = client.post("/recipes/", json=payload, headers=headers)
    print(resp.get_json())
    data = resp.get_json()
    assert resp.status_code == 201
    assert data["recipe"]["title"] == "Salad"

# -------------------------
# Recipe Delete Tests
# -------------------------
def test_delete_recipe_nonexistent(client, test_user, auth_headers):
    headers = auth_headers(test_user.id)
    resp = client.delete("/recipes/9999", headers=headers)
    assert resp.status_code == 404

def test_delete_recipe_success(client, test_user, auth_headers, db):
    headers = auth_headers(test_user.id)
    recipe = Recipe(title="Temp", ingredients="X", instructions="Y", user_id=test_user.id)
    db.session.add(recipe)
    db.session.commit()
    resp = client.delete(f"/recipes/{recipe.id}", headers=headers)
    assert resp.status_code == 200

# -------------------------
# Recipe List Tests
# -------------------------
def test_list_recipes(client, test_user, auth_headers, db):
    headers = auth_headers(test_user.id)
    r1 = Recipe(title="R1", ingredients="A", instructions="B", user_id=test_user.id)
    r2 = Recipe(title="R2", ingredients="C", instructions="D", user_id=test_user.id)
    db.session.add_all([r1, r2])
    db.session.commit()
    resp = client.get("/recipes/", headers=headers)
    data = resp.get_json()
    assert resp.status_code == 200
    assert len(data) >= 2
