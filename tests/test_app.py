"""
Tests for the Mergington High School API
"""

from fastapi.testclient import TestClient
from urllib.parse import quote
from src.app import app

client = TestClient(app)


def test_get_activities():
    """Test retrieving all activities"""
    # Arrange - No special setup needed as activities are in-memory

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data

    # Check structure of one activity
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)


def test_signup_for_activity():
    """Test signing up a student for an activity"""
    # Arrange
    email = "newstudent@mergington.edu"
    activity = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    result = response.json()
    assert "message" in result
    assert email in result["message"]

    # Verify the participant was added
    response = client.get("/activities")
    data = response.json()
    assert email in data[activity]["participants"]


def test_signup_activity_not_found():
    """Test signing up for a non-existent activity"""
    # Arrange
    email = "student@mergington.edu"
    activity = "NonExistent Club"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    result = response.json()
    assert "detail" in result
    assert "Activity not found" in result["detail"]


def test_unregister_from_activity():
    """Test unregistering a student from an activity"""
    # Arrange
    email = "michael@mergington.edu"  # Already in Chess Club
    activity = "Chess Club"

    # Act
    response = client.delete(f"/activities/{quote(activity)}/participants/{quote(email)}")

    # Assert
    assert response.status_code == 200
    result = response.json()
    assert "message" in result
    assert email in result["message"]

    # Verify the participant was removed
    response = client.get("/activities")
    data = response.json()
    assert email not in data[activity]["participants"]


def test_unregister_activity_not_found():
    """Test unregistering from a non-existent activity"""
    # Arrange
    email = "student@mergington.edu"
    activity = "NonExistent Club"

    # Act
    response = client.delete(f"/activities/{quote(activity)}/participants/{quote(email)}")

    # Assert
    assert response.status_code == 404
    result = response.json()
    assert "detail" in result
    assert "Activity not found" in result["detail"]


def test_unregister_participant_not_found():
    """Test unregistering a student not in the activity"""
    # Arrange
    email = "notenrolled@mergington.edu"
    activity = "Chess Club"

    # Act
    response = client.delete(f"/activities/{quote(activity)}/participants/{quote(email)}")

    # Assert
    assert response.status_code == 404
    result = response.json()
    assert "detail" in result
    assert "Participant not found" in result["detail"]


def test_signup_allows_duplicates():
    """Test that signing up the same email multiple times is not allowed"""
    # Arrange
    email = "duplicatestudent@mergington.edu"
    activity = "Programming Class"

    # Act - Sign up once
    response1 = client.post(f"/activities/{activity}/signup?email={email}")
    # Sign up again
    response2 = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert - First succeeds, second fails
    assert response1.status_code == 200
    assert response2.status_code == 400
    result = response2.json()
    assert "detail" in result
    assert "Student already signed up" in result["detail"]

    # Verify only one instance
    response = client.get("/activities")
    data = response.json()
    count = data[activity]["participants"].count(email)
    assert count == 1