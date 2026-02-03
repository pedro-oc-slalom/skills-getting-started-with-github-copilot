import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)
INITIAL_ACTIVITIES = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    """Ensure each test starts from a known snapshot of activities."""
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))
    yield
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))


def test_get_activities_returns_all_records():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert set(data.keys()) == set(INITIAL_ACTIVITIES.keys())


def test_signup_for_activity_adds_participant():
    email = "newstudent@mergington.edu"
    response = client.post("/activities/Chess Club/signup", params={"email": email})
    assert response.status_code == 200
    assert email in activities["Chess Club"]["participants"]


def test_signup_for_activity_prevents_duplicates():
    existing_email = INITIAL_ACTIVITIES["Chess Club"]["participants"][0]
    response = client.post("/activities/Chess Club/signup", params={"email": existing_email})
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant_succeeds():
    email = INITIAL_ACTIVITIES["Gym Class"]["participants"][0]
    response = client.delete("/activities/Gym Class/participants", params={"email": email})
    assert response.status_code == 200
    assert email not in activities["Gym Class"]["participants"]


def test_remove_participant_handles_missing_student():
    email = "notregistered@mergington.edu"
    response = client.delete("/activities/Gym Class/participants", params={"email": email})
    assert response.status_code == 404
    assert response.json()["detail"] == "Student not registered for this activity"
