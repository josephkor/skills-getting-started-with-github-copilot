import copy
import pytest
from fastapi import HTTPException
import app

@pytest.fixture
def restore_activities():
    original = copy.deepcopy(app.activities)
    try:
        yield
    finally:
        app.activities.clear()
        app.activities.update(original)

def test_signup_success(restore_activities):
    activity = "Chess Club"
    email = "testuser@example.com"
    assert email not in app.activities[activity]["participants"]
    result = app.signup_for_activity(activity, email)
    assert result == {"message": f"Signed up {email} for {activity}"}
    assert email in app.activities[activity]["participants"]

def test_signup_activity_not_found(restore_activities):
    with pytest.raises(HTTPException) as excinfo:
        app.signup_for_activity("Nonexistent Activity", "noone@example.com")
    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == "Activity not found"