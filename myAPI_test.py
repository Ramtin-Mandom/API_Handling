from fastapi.testclient import TestClient
from myAPI import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "API is running"}

def test_analyze_text():
    response = client.post(
        "/analyze-text",
        json={"text": "hello", "c": "l"}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["input_text"] == "hello"
    assert data["char_count"] == 5
    assert data["c_count"] == 2
    assert data["ratio"] == 2 / 5

def test_empty_text():
    response = client.post(
        "/analyze-text",
        json={"text": "", "c": "a"}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["char_count"] == 0
    assert data["c_count"] == 0
    assert data["ratio"] == 0.0

def test_invalid_character():
    response = client.post(
        "/analyze-text",
        json={"text": "hello", "c": "ll"}
    )

    assert response.status_code == 422

def test_non_string_text():
    response = client.post(
        "/analyze-text",
        json={"text": 123, "c": "a"}
    )

    assert response.status_code == 422