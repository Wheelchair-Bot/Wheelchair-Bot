"""Tests for the main API endpoints."""

from fastapi.testclient import TestClient
from wheelchair_bot.main import app

client = TestClient(app)


def test_root():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Wheelchair Bot API"
    assert data["status"] == "running"
    assert "version" in data


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_get_status():
    """Test status endpoint."""
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert "battery_level" in data
    assert "is_moving" in data
    assert "speed" in data
    assert "direction" in data


def test_move_valid():
    """Test move endpoint with valid parameters."""
    response = client.post("/api/move?direction=forward&speed=50")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["command"] == "forward"
    assert data["speed"] == 50


def test_move_invalid_direction():
    """Test move endpoint with invalid direction."""
    response = client.post("/api/move?direction=invalid&speed=50")
    assert response.status_code == 200
    data = response.json()
    assert "error" in data


def test_move_invalid_speed():
    """Test move endpoint with invalid speed."""
    response = client.post("/api/move?direction=forward&speed=150")
    assert response.status_code == 200
    data = response.json()
    assert "error" in data
