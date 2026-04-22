import pytest
import services

from models import (
    OpenAIInput,
    OpenAIRequest,
    OpenAIResponse,
    OpenAIEvaluatedResponse,
    OpenAIFinalResult,
)


# ---------------------------
# Helpers (Mock OpenAI)
# ---------------------------

class FakeResponse:
    def __init__(self, output_text):
        self.output_text = output_text


class FakeResponsesAPI:
    def __init__(self, outputs):
        self.outputs = outputs
        self.call_index = 0

    def create(self, model, input):
        result = self.outputs[self.call_index]
        self.call_index += 1

        if isinstance(result, Exception):
            raise result

        return FakeResponse(result)


class FakeOpenAIClient:
    def __init__(self, outputs):
        self.responses = FakeResponsesAPI(outputs)


# ---------------------------
# openai_request_process
# ---------------------------

def test_process_success():
    data = OpenAIInput(text="paper text")
    result = services.openai_request_process(data)

    assert isinstance(result, OpenAIRequest)
    assert len(result.requests) > 0


def test_process_empty_text():
    with pytest.raises(services.InputProcessingError):
        services.openai_request_process(OpenAIInput(text="   "))


def test_process_none():
    with pytest.raises(services.InputProcessingError):
        services.openai_request_process(None)


# ---------------------------
# openai_request
# ---------------------------

def test_openai_request_success(monkeypatch):
    monkeypatch.setattr(
        services,
        "_get_openai_client",
        lambda: FakeOpenAIClient(["s1", "s2"])
    )

    result = services.openai_request(
        OpenAIRequest(requests=["r1", "r2"])
    )

    assert result.responses == ["s1", "s2"]


def test_openai_request_failure(monkeypatch):
    monkeypatch.setattr(
        services,
        "_get_openai_client",
        lambda: FakeOpenAIClient(["s1", Exception("fail")])
    )

    with pytest.raises(services.OpenAIRequestError):
        services.openai_request(OpenAIRequest(requests=["r1", "r2"]))


# ---------------------------
# evaluate_openai_response
# ---------------------------

def test_evaluate_success(monkeypatch):
    monkeypatch.setattr(
        services,
        "_get_openai_client",
        lambda: FakeOpenAIClient(["1"])
    )

    result = services.evaluate_openai_response(
        OpenAIResponse(responses=["a", "b"])
    )

    assert result.analysis_result == 1


def test_evaluate_invalid_output(monkeypatch):
    monkeypatch.setattr(
        services,
        "_get_openai_client",
        lambda: FakeOpenAIClient(["invalid"])
    )

    with pytest.raises(services.EvaluationError):
        services.evaluate_openai_response(
            OpenAIResponse(responses=["a", "b"])
        )


# ---------------------------
# final_clean_up
# ---------------------------

def test_final_cleanup_success():
    result = services.final_clean_up(
        OpenAIEvaluatedResponse(analysis_result=1),
        OpenAIResponse(responses=["a", "b"])
    )

    assert result.final_text == "a"


def test_final_cleanup_invalid_index():
    with pytest.raises(services.FinalCleanupError):
        services.final_clean_up(
            OpenAIEvaluatedResponse(analysis_result=10),
            OpenAIResponse(responses=["a"])
        )


def test_final_cleanup_empty():
    with pytest.raises(services.FinalCleanupError):
        services.final_clean_up(
            OpenAIEvaluatedResponse(analysis_result=1),
            OpenAIResponse(responses=[])
        )