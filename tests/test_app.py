"""Tests for the Mergington High School API"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

client = TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    from app import activities
    initial_activities = {
        "Basketball Team": {
            "description": "Competitive basketball team with regular practices and games",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Tennis coaching and match play for all skill levels",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["jordan@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop public speaking and argumentation skills",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 10,
            "participants": ["sarah@mergington.edu"]
        },
        "Science Olympiad": {
            "description": "Compete in science and engineering challenges",
            "schedule": "Saturdays, 10:00 AM - 12:00 PM",
            "max_participants": 15,
            "participants": ["chris@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in school plays and theatrical productions",
            "schedule": "Mondays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["lucas@mergington.edu", "avery@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and sculpture techniques",
            "schedule": "Tuesdays and Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["maya@mergington.edu"]
        },
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }
    
    activities.clear()
    activities.update(initial_activities)
    yield
    activities.clear()
    activities.update(initial_activities)


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, reset_activities):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Basketball Team" in data
        assert "Tennis Club" in data
        assert len(data) == 9

    def test_get_activities_contains_required_fields(self, reset_activities):
        """Test that each activity contains required fields"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Basketball Team"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_new_participant_success(self, reset_activities):
        """Test successfully signing up a new participant"""
        response = client.post(
            "/activities/Basketball%20Team/signup?email=newstudent@mergington.edu",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]

        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Basketball Team"]["participants"]

    def test_signup_duplicate_participant_fails(self, reset_activities):
        """Test that signing up with duplicate email fails"""
        response = client.post(
            "/activities/Basketball%20Team/signup?email=alex@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_nonexistent_activity_fails(self, reset_activities):
        """Test that signing up for non-existent activity fails"""
        response = client.post(
            "/activities/NonExistent%20Activity/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]

    def test_signup_multiple_participants(self, reset_activities):
        """Test signing up multiple different participants"""
        emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
        
        for email in emails:
            response = client.post(
                f"/activities/Basketball%20Team/signup?email={email}"
            )
            assert response.status_code == 200

        # Verify all were added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        participants = activities_data["Basketball Team"]["participants"]
        
        for email in emails:
            assert email in participants


class TestUnregister:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_existing_participant_success(self, reset_activities):
        """Test successfully unregistering an existing participant"""
        response = client.delete(
            "/activities/Basketball%20Team/unregister?email=alex@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]

        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "alex@mergington.edu" not in activities_data["Basketball Team"]["participants"]

    def test_unregister_nonexistent_participant_fails(self, reset_activities):
        """Test that unregistering non-existent participant fails"""
        response = client.delete(
            "/activities/Basketball%20Team/unregister?email=nonexistent@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"]

    def test_unregister_nonexistent_activity_fails(self, reset_activities):
        """Test that unregistering from non-existent activity fails"""
        response = client.delete(
            "/activities/NonExistent%20Activity/unregister?email=alex@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]

    def test_unregister_then_signup_again(self, reset_activities):
        """Test that a participant can unregister and signup again"""
        email = "alex@mergington.edu"
        activity = "Basketball%20Team"

        # Unregister
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 200

        # Sign up again
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200

        # Verify participant is back
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data["Basketball Team"]["participants"]


class TestIntegration:
    """Integration tests for complete workflows"""

    def test_full_signup_and_unregister_workflow(self, reset_activities):
        """Test the complete workflow of signing up and unregistering"""
        email = "testuser@mergington.edu"
        activity = "Tennis%20Club"

        # 1. Sign up
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup_response.status_code == 200

        # 2. Verify in activities list
        activities_response = client.get("/activities")
        assert email in activities_response.json()["Tennis Club"]["participants"]

        # 3. Unregister
        unregister_response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert unregister_response.status_code == 200

        # 4. Verify removed from activities list
        activities_response = client.get("/activities")
        assert email not in activities_response.json()["Tennis Club"]["participants"]

    def test_multiple_activities_signup(self, reset_activities):
        """Test signing up for multiple activities"""
        email = "multiactivity@mergington.edu"
        activities_list = ["Basketball%20Team", "Chess%20Club", "Drama%20Club"]

        # Sign up for multiple activities
        for activity in activities_list:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200

        # Verify in all activities
        activities_response = client.get("/activities")
        data = activities_response.json()
        for activity in ["Basketball Team", "Chess Club", "Drama Club"]:
            assert email in data[activity]["participants"]
