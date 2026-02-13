"""Tests for the FastAPI application"""
import pytest


class TestGetActivities:
    """Test cases for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert "Basketball" in data
        assert "Tennis Club" in data
        assert "Debate Team" in data
        
    def test_get_activities_contains_activity_details(self, client):
        """Test that activities contain expected fields"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Basketball"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        
    def test_get_activities_basketball_has_initial_participant(self, client):
        """Test that Basketball activity has initial participant"""
        response = client.get("/activities")
        data = response.json()
        assert "alex@mergington.edu" in data["Basketball"]["participants"]


class TestSignupForActivity:
    """Test cases for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_successful(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Basketball/signup?email=john@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        
    def test_signup_adds_participant(self, client):
        """Test that signup actually adds participant to activity"""
        client.post("/activities/Basketball/signup?email=john@mergington.edu")
        response = client.get("/activities")
        participants = response.json()["Basketball"]["participants"]
        assert "john@mergington.edu" in participants
        
    def test_signup_duplicate_fails(self, client):
        """Test that signup fails for already registered student"""
        # First signup should succeed
        response1 = client.post(
            "/activities/Basketball/signup?email=new@mergington.edu"
        )
        assert response1.status_code == 200
        
        # Second signup with same email should fail
        response2 = client.post(
            "/activities/Basketball/signup?email=new@mergington.edu"
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]
        
    def test_signup_nonexistent_activity_fails(self, client):
        """Test that signup fails for nonexistent activity"""
        response = client.post(
            "/activities/Nonexistent/signup?email=john@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
        
    def test_signup_multiple_participants(self, client):
        """Test that multiple participants can signup for same activity"""
        response1 = client.post(
            "/activities/Basketball/signup?email=student1@mergington.edu"
        )
        response2 = client.post(
            "/activities/Basketball/signup?email=student2@mergington.edu"
        )
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        response = client.get("/activities")
        participants = response.json()["Basketball"]["participants"]
        assert len(participants) == 3  # alex + 2 new students


class TestUnregisterFromActivity:
    """Test cases for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_successful(self, client):
        """Test successful unregistration from an activity"""
        response = client.delete(
            "/activities/Basketball/unregister?email=alex@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        
    def test_unregister_removes_participant(self, client):
        """Test that unregister actually removes participant"""
        client.delete(
            "/activities/Basketball/unregister?email=alex@mergington.edu"
        )
        response = client.get("/activities")
        participants = response.json()["Basketball"]["participants"]
        assert "alex@mergington.edu" not in participants
        
    def test_unregister_not_registered_fails(self, client):
        """Test that unregister fails for non-registered student"""
        response = client.delete(
            "/activities/Basketball/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
        
    def test_unregister_nonexistent_activity_fails(self, client):
        """Test that unregister fails for nonexistent activity"""
        response = client.delete(
            "/activities/Nonexistent/unregister?email=alex@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
        
    def test_signup_then_unregister(self, client):
        """Test complete signup and unregister flow"""
        # Sign up
        response1 = client.post(
            "/activities/Tennis Club/signup?email=newuser@mergington.edu"
        )
        assert response1.status_code == 200
        
        # Verify signup
        response = client.get("/activities")
        assert "newuser@mergington.edu" in response.json()["Tennis Club"]["participants"]
        
        # Unregister
        response2 = client.delete(
            "/activities/Tennis Club/unregister?email=newuser@mergington.edu"
        )
        assert response2.status_code == 200
        
        # Verify unregister
        response = client.get("/activities")
        assert "newuser@mergington.edu" not in response.json()["Tennis Club"]["participants"]


class TestActivityParticipantCount:
    """Test cases for participant count tracking"""
    
    def test_participant_count_includes_all(self, client):
        """Test that participant count is accurate"""
        response = client.get("/activities")
        data = response.json()
        
        # Debate Team has 2 participants initially
        assert len(data["Debate Team"]["participants"]) == 2
        assert data["Debate Team"]["participants"] == ["lucas@mergington.edu", "sarah@mergington.edu"]
        
    def test_participant_count_after_signup(self, client):
        """Test that participant count updates after signup"""
        # Initial count
        response1 = client.get("/activities")
        initial_count = len(response1.json()["Basketball"]["participants"])
        
        # Sign up new participant
        client.post(
            "/activities/Basketball/signup?email=newuser@mergington.edu"
        )
        
        # Check updated count
        response2 = client.get("/activities")
        updated_count = len(response2.json()["Basketball"]["participants"])
        assert updated_count == initial_count + 1
