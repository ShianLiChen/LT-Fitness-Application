from models.workout import Workout
from datetime import datetime

# -------------------------
# Create Workout Tests
# -------------------------
def test_create_workout_missing_name(client, test_user, auth_headers):
    headers = auth_headers(test_user.id)
    resp = client.post("/workouts/", json={}, headers=headers)
    data = resp.get_json()
    assert resp.status_code == 400
    assert data is not None
    assert "error" in data

def test_create_workout_success(client, test_user, auth_headers):
    headers = auth_headers(test_user.id)
    payload = {
        "exercise_name": "Pushups",
        "duration_minutes": 20,
        "start_time": datetime.utcnow().isoformat()
    }
    resp = client.post("/workouts/", json=payload, headers=headers)
    data = resp.get_json()
    assert resp.status_code == 201
    assert data["workout"]["exercise_name"] == "Pushups"

# -------------------------
# Get Workouts Tests
# -------------------------
def test_get_workouts_empty(client, test_user, auth_headers):
    headers = auth_headers(test_user.id)
    resp = client.get("/workouts/", headers=headers)
    data = resp.get_json()
    assert resp.status_code == 200
    assert isinstance(data["workouts"], list)

def test_get_workout_success(client, test_user, auth_headers, db):
    headers = auth_headers(test_user.id)

    workout = Workout(
        user_id=test_user.id,
        exercise_name="Running",
        duration_minutes=15,
        calories_burned=90
    )
    db.session.add(workout)
    db.session.commit()

    resp = client.get(f"/workouts/{workout.id}", headers=headers)
    data = resp.get_json()

    assert resp.status_code == 200
    assert data["workout"]["exercise_name"] == "Running"

# -------------------------
# Update Workout Tests
# -------------------------
def test_update_nonexistent_workout(client, test_user, auth_headers):
    headers = auth_headers(test_user.id)
    resp = client.put("/workouts/9999", json={"duration_minutes": 30}, headers=headers)
    data = resp.get_json()
    assert resp.status_code == 404
    assert data is not None
    assert "error" in data

def test_update_workout_success(client, test_user, auth_headers, db):
    headers = auth_headers(test_user.id)

    workout = Workout(
        user_id=test_user.id,
        exercise_name="Cycling",
        duration_minutes=10,
        calories_burned=60
    )
    db.session.add(workout)
    db.session.commit()

    payload = {"exercise_name": "Indoor Cycling"}

    resp = client.put(f"/workouts/{workout.id}", headers=headers, json=payload)
    data = resp.get_json()

    assert resp.status_code == 200
    assert "updated" in data["message"].lower()
# -------------------------
# Delete Workout Tests
# -------------------------
def test_delete_nonexistent_workout(client, test_user, auth_headers):
    headers = auth_headers(test_user.id)
    resp = client.delete("/workouts/9999", headers=headers)
    data = resp.get_json()
    assert resp.status_code == 404
    assert data is not None
    assert "error" in data

def test_delete_workout_success(client, test_user, auth_headers, db):
    headers = auth_headers(test_user.id)

    workout = Workout(
        user_id=test_user.id,
        exercise_name="Burpees",
        duration_minutes=10,
        calories_burned=60
    )
    db.session.add(workout)
    db.session.commit()

    resp = client.delete(f"/workouts/{workout.id}", headers=headers)

    assert resp.status_code == 200

# -------------------------
# Batch Workout Tests
# -------------------------
def test_batch_create_workouts_success(client, test_user, auth_headers):
    headers = auth_headers(test_user.id)

    payload = [
        {"exercise_name": "Pushups", "sets": 3, "duration_minutes": 20},
        {"exercise_name": "Pullups", "sets": 4, "duration_minutes": 15}
    ]

    resp = client.post("/workouts/batch", headers=headers, json=payload)
    data = resp.get_json()

    assert resp.status_code == 201
    assert data["count"] == 2


def test_batch_create_invalid(client, test_user, auth_headers):
    headers = auth_headers(test_user.id)

    resp = client.post("/workouts/batch", headers=headers, json=None)

    assert resp.status_code == 400