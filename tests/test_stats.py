from datetime import datetime
from models.workout import Workout
from models.recipe import Recipe


# -------------------------
# Stats UI Tests
# -------------------------
def test_stats_page_requires_login(client):
    """
    Verify that the stats UI page requires login and redirects appropriately.
    """
    resp = client.get("/stats/ui")
    assert resp.status_code == 200
    assert b'href="/login"' in resp.data


# -------------------------
# Stats API Tests
# -------------------------
def test_get_stats_data_empty(client, test_user, auth_headers):
    """
    Verify that stats API returns zero values when no workouts or recipes exist.
    """
    headers = auth_headers(test_user.id)
    resp = client.get("/stats/api/data", headers=headers)
    data = resp.get_json()

    assert data is not None
    assert data["burned"] == [0] * 7
    assert data["consumed"] == [0] * 7


def test_get_stats_data_with_entries(client, test_user, auth_headers, db):
    """
    Verify that stats API correctly returns calories burned and consumed when
    there are workout and recipe entries for the user.
    """
    headers = auth_headers(test_user.id)
    today = datetime.utcnow()

    # Create workout and recipe entries for today
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

    # Call stats API
    resp = client.get("/stats/api/data", headers=headers)
    data = resp.get_json()

    # Verify returned data
    assert data is not None
    assert data["burned"][6] == 100  # today
    assert data["consumed"][6] == 150
