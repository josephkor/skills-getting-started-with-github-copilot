import copy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the in-memory activities state before each test."""
    baseline = copy.deepcopy(app_module.activities)
    yield
    # restore baseline after test
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(baseline))


@pytest.fixture()
def client():
    return TestClient(app_module.app)


def test_get_activities(client):
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # expect some known activities from the seed data
    assert "Chess Club" in data


def test_signup_and_presence(client):
    activity = "Chess Club"
    email = "testuser@example.com"

    # ensure email not present
    before = client.get("/activities").json()
    assert email not in before[activity]["participants"]

    # signup
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert "Signed up" in resp.json().get("message", "")

    # verify presence
    after = client.get("/activities").json()
    assert email in after[activity]["participants"]


def test_signup_duplicate_fails(client):
    activity = "Chess Club"
    email = "dup@example.com"

    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200

    # second signup should fail with 400
    resp2 = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp2.status_code == 400


def test_unregister_removes_participant(client):
    activity = "Programming Class"
    email = "remove_me@example.com"

    # add the participant first
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200

    # now unregister
    resp2 = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert resp2.status_code == 200
    assert "Unregistered" in resp2.json().get("message", "")

    # confirm removed
    after = client.get("/activities").json()
    assert email not in after[activity]["participants"]


def test_unregister_nonexistent_returns_404(client):
    activity = "Gym Class"
    email = "doesnotexist@example.com"

    resp = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert resp.status_code == 404
