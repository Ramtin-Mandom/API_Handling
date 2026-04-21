from models import InputText

from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from models import (
    OpenAIInput,
    OpenAIRequest,
    OpenAIResponse,
    OpenAIAnalysisResponse,
)


def openai_request_clean_up(data: OpenAIInput) -> OpenAIRequest:
    """
    Converts the API input model into the model used for the OpenAI request step.
    """
    return OpenAIRequest(request=data.input)


def openai_request(data: OpenAIRequest) -> OpenAIResponse:
    """
    Sends the request to OpenAI and returns the raw response wrapped
    in the OpenAIResponse model.
    """
    root_dir = Path(__file__).resolve().parent
    env_file = root_dir / ".env"

    if not env_file.is_file():
        raise FileNotFoundError(
            "Missing .env next to services.py. "
            "Create a .env file and add OPENAI_API_KEY=your_key_here"
        )

    load_dotenv(env_file)

    client = OpenAI()

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=data.request,
    )

    return OpenAIResponse(response=response.output_text)


def analyze_openai_response(data: OpenAIResponse) -> OpenAIAnalysisResponse:
    """
    Final processing step. Right now it simply passes the response through,
    but later you can add formatting, summarization, filtering, etc.
    """
    return OpenAIAnalysisResponse(analysis_result=data.response)

def analyze_text(data: InputText) -> dict:
    char_count = len(data.text)
    c_count = data.text.count(data.c)
    ratio = c_count / char_count if char_count > 0 else 0.0

    return {
        "input_text": data.text,
        "char_count": char_count,
        "c_count": c_count,
        "ratio": ratio
    }
