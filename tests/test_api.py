import pytest
from fastapi.testclient import TestClient

from myAPI import app
from models import (
    OpenAIRequest,
    OpenAIResponse,
    OpenAIEvaluatedResponse,
    OpenAIFinalResult,
)

client = TestClient(app)


# ---------------------------
# Basic API tests
# ---------------------------

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "API is running"}


def test_hello():
    response = client.get("/hello/Ramtin")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, Ramtin"}


# ---------------------------
# Main endpoint (mock services)
# ---------------------------

def test_openai_endpoint_success(monkeypatch):
    def fake_process(data):
        return OpenAIRequest(requests=["req1", "req2"])

    def fake_openai_request(data):
        return OpenAIResponse(responses=["summary 1", "summary 2"])

    def fake_evaluate(data):
        return OpenAIEvaluatedResponse(analysis_result=2)

    def fake_final(evaluation, data):
        return OpenAIFinalResult(final_text="summary 2")

    monkeypatch.setattr("myAPI.openai_request_process", fake_process)
    monkeypatch.setattr("myAPI.openai_request", fake_openai_request)
    monkeypatch.setattr("myAPI.evaluate_openai_response", fake_evaluate)
    monkeypatch.setattr("myAPI.final_clean_up", fake_final)

    response = client.post("/openai-request", json={"text": "test"})
    assert response.status_code == 200
    assert response.json() == {"final_text": "summary 2"}


def test_openai_endpoint_missing_text():
    response = client.post("/openai-request", json={})
    assert response.status_code == 422


def test_openai_endpoint_wrong_type():
    response = client.post("/openai-request", json={"text": 123})
    assert response.status_code == 422