from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from models import (
    OpenAIInput,
    OpenAIRequest,
    OpenAIResponse,
    OpenAIEvaluatedResponse,
    OpenAIFinalResult,
)

from prompts import(
    prompts,
    template,
    evaluation_prompt_beginning,
    evaluation_prompt_ending,
)


def openai_request_process(data: OpenAIInput) -> OpenAIRequest:
    """
    Converts the API input model into the model used for the OpenAI request step.
    """
    processedInputs = []
    for prompt in prompts:
        processedInputs.append(
            f"Request:\n{prompt}\n\nTemplate:\n{template}\n\nPaper:\n{data.text}"
        )
    return OpenAIRequest(requests= processedInputs)


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

    responses = []

    for request in data.requests:
        try:
            response = client.responses.create(
                model="gpt-4.1-mini",
                input=request,
            )
            responses.append(response.output_text)
        except Exception as e:
            responses.append(f"ERROR: {str(e)}")
    return OpenAIResponse(responses=responses)

def evaluate_openai_response(data: OpenAIResponse) -> OpenAIEvaluatedResponse:
    eval_prompt = evaluation_prompt_beginning + "\n\n"

    for i, summary in enumerate(data.responses, start=1):
        eval_prompt += f"Summary {i}:\n{summary}\n\n"

    eval_prompt += evaluation_prompt_ending

    root_dir = Path(__file__).resolve().parent
    env_file = root_dir / ".env"

    if not env_file.is_file():
        raise FileNotFoundError(
            "Missing .env next to services.py. "
            "Create a .env file and add OPENAI_API_KEY=your_key_here"
        )

    load_dotenv(env_file)
    client = OpenAI()

    evaluation = client.responses.create(
        model="gpt-4.1-mini",
        input=eval_prompt,
    )

    evaluation_text = evaluation.output_text.strip()

    # Check it's purely digits
    if not evaluation_text.isdigit():
        raise ValueError(f"Invalid evaluation output: '{evaluation_text}'")

    analysis_result = int(evaluation_text)

    return OpenAIEvaluatedResponse(analysis_result=analysis_result)

def final_clean_up(evaluation: OpenAIEvaluatedResponse, data: OpenAIResponse) -> OpenAIFinalResult:
    index = evaluation.analysis_result - 1

    if not isinstance(data.responses, list):
        raise TypeError("data.responses must be a list of summaries")

    if index < 0 or index >= len(data.responses):
        raise ValueError(f"Invalid summary index: {evaluation.analysis_result}")

    text = data.responses[index]
    return OpenAIFinalResult(final_text=text)