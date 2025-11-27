from datetime import datetime
from models.workout import Workout
from models.recipe import Recipe

# -------------------------
# Stats UI Tests
# -------------------------
def test_stats_page_requires_login(client):
    resp = client.get("/stats/ui")
    assert resp.status_code == 200
    assert b'href="/login"' in resp.data

# -------------------------
# Stats API Tests
# -------------------------
def test_get_stats_data_empty(client, test_user, auth_headers):
    headers = auth_headers(test_user.id)
    resp = client.get("/stats/api/data", headers=headers)
    data = resp.get_json()
    assert data is not None
    assert data["burned"] == [0] * 7
    assert data["consumed"] == [0] * 7

def test_get_stats_data_with_entries(client, test_user, auth_headers, db):
    headers = auth_headers(test_user.id)
    today = datetime.utcnow()
    w = Workout(
        user_id=test_user.id,
        exercise_name="Pushups",
        start_time=today,
        calories_burned=100
    )
    r = Recipe(
        user_id=test_user.id,
        title="Salad",
        ingredients="Lettuce",
        instructions="Mix",
        calories=150
    )
    db.session.add_all([w, r])
    db.session.commit()

    resp = client.get("/stats/api/data", headers=headers)
    data = resp.get_json()
    assert data is not None
    assert data["burned"][6] == 100  # today
    assert data["consumed"][6] == 150
