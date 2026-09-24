"""Unit tests for FastAPI endpoints."""
import pytest
from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True
    assert data["scaler_loaded"] is True
    assert data["feature_count"] == 22


def test_predict_single_endpoint():
    payload = {
        "Age": 22,
        "Gender": "Male",
        "Location": "USA",
        "GameGenre": "RPG",
        "GameDifficulty": "Medium",
        "PlayTimeHours": 14.2,
        "InGamePurchases": 1,
        "SessionsPerWeek": 4,
        "AvgSessionDurationMinutes": 32.0,
        "PlayerLevel": 15,
        "AchievementsUnlocked": 8
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "churn_probability" in data
    assert 0.0 <= data["churn_probability"] <= 1.0
    assert data["risk_tier"] in ["Critical Risk", "Medium Risk", "Low Risk"]
    assert len(data["recommended_action"]) > 0


def test_predict_batch_endpoint():
    payload = {
        "players": [
            {
                "Age": 20,
                "Gender": "Female",
                "Location": "Europe",
                "GameGenre": "Action",
                "GameDifficulty": "Easy",
                "PlayTimeHours": 2.0,
                "InGamePurchases": 0,
                "SessionsPerWeek": 1,
                "AvgSessionDurationMinutes": 15.0,
                "PlayerLevel": 2,
                "AchievementsUnlocked": 1
            },
            {
                "Age": 30,
                "Gender": "Male",
                "Location": "Asia",
                "GameGenre": "Strategy",
                "GameDifficulty": "Hard",
                "PlayTimeHours": 22.0,
                "InGamePurchases": 1,
                "SessionsPerWeek": 8,
                "AvgSessionDurationMinutes": 75.0,
                "PlayerLevel": 45,
                "AchievementsUnlocked": 30
            }
        ]
    }
    response = client.post("/predict/batch", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_processed"] == 2
    assert len(data["results"]) == 2
