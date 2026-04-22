from pathlib import Path
from typing import List

from dotenv import load_dotenv
from openai import OpenAI

from models import (
    OpenAIInput,
    OpenAIRequest,
    OpenAIResponse,
    OpenAIEvaluatedResponse,
    OpenAIFinalResult,
)

from prompts import (
    prompts,
    template,
    evaluation_prompt_beginning,
    evaluation_prompt_ending,
)


class ServiceError(Exception):
    """Base exception for service-layer errors."""
    pass


class InputProcessingError(ServiceError):
    """Raised when API input cannot be processed safely."""
    pass


class ConfigurationError(ServiceError):
    """Raised when required config like .env or API key is missing."""
    pass


class OpenAIRequestError(ServiceError):
    """Raised when a request to OpenAI fails."""
    pass


class EvaluationError(ServiceError):
    """Raised when the evaluator response is invalid."""
    pass


class FinalCleanupError(ServiceError):
    """Raised when final summary selection fails."""
    pass


def _get_openai_client() -> OpenAI:
    """
    Loads environment variables and returns an initialized OpenAI client.
    Raises ConfigurationError if setup is invalid.
    """
    root_dir = Path(__file__).resolve().parent
    env_file = root_dir / ".env"

    if not env_file.is_file():
        raise ConfigurationError(
            "Missing .env next to services.py. "
            "Create a .env file and add OPENAI_API_KEY=your_key_here"
        )

    load_dotenv(env_file)

    import os
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key or not api_key.strip():
        raise ConfigurationError(
            "OPENAI_API_KEY is missing or empty in the .env file."
        )

    try:
        client = OpenAI(api_key=api_key)
    except Exception as e:
        raise ConfigurationError(
            f"Failed to initialize OpenAI client: {str(e)}"
        ) from e

    return client


def openai_request_process(data: OpenAIInput) -> OpenAIRequest:
    """
    Converts API input into the prompt list used for the OpenAI request step.
    """
    if data is None:
        raise InputProcessingError("Input data cannot be None.")

    if not isinstance(data.text, str):
        raise InputProcessingError("Input text must be a string.")

    cleaned_text = data.text.strip()
    if not cleaned_text:
        raise InputProcessingError("Input text cannot be empty.")

    if not isinstance(prompts, list) or not prompts:
        raise InputProcessingError("Prompt list is missing or empty.")

    if not isinstance(template, str) or not template.strip():
        raise InputProcessingError("Template is missing or empty.")

    processed_inputs: List[str] = []

    try:
        for i, prompt in enumerate(prompts, start=1):
            if not isinstance(prompt, str) or not prompt.strip():
                raise InputProcessingError(
                    f"Prompt {i} is invalid or empty."
                )

            full_request = (
                f"Request:\n{prompt.strip()}\n\n"
                f"Template:\n{template.strip()}\n\n"
                f"Paper:\n{cleaned_text}"
            )
            processed_inputs.append(full_request)

    except Exception as e:
        if isinstance(e, InputProcessingError):
            raise
        raise InputProcessingError(
            f"Failed to process OpenAI input: {str(e)}"
        ) from e

    if not processed_inputs:
        raise InputProcessingError("No processed requests were created.")

    return OpenAIRequest(requests=processed_inputs)


def openai_request(data: OpenAIRequest) -> OpenAIResponse:
    """
    Sends all prompt variations to OpenAI and returns their raw summaries.
    Fails if any request fails, instead of mixing real summaries with error text.
    """
    if data is None:
        raise OpenAIRequestError("OpenAI request data cannot be None.")

    if not isinstance(data.requests, list):
        raise OpenAIRequestError("data.requests must be a list of strings.")

    if not data.requests:
        raise OpenAIRequestError("data.requests cannot be empty.")

    for i, request in enumerate(data.requests, start=1):
        if not isinstance(request, str) or not request.strip():
            raise OpenAIRequestError(f"Request {i} is invalid or empty.")

    client = _get_openai_client()
    responses: List[str] = []

    for i, request in enumerate(data.requests, start=1):
        try:
            response = client.responses.create(
                model="gpt-4.1-mini",
                input=request,
            )

            output_text = getattr(response, "output_text", None)

            if not isinstance(output_text, str) or not output_text.strip():
                raise OpenAIRequestError(
                    f"OpenAI returned an empty response for request {i}."
                )

            responses.append(output_text.strip())

        except OpenAIRequestError:
            raise
        except Exception as e:
            raise OpenAIRequestError(
                f"OpenAI request failed for request {i}: {str(e)}"
            ) from e

    if not responses:
        raise OpenAIRequestError("No OpenAI responses were received.")

    if len(responses) != len(data.requests):
        raise OpenAIRequestError(
            "Mismatch between number of requests and responses."
        )

    return OpenAIResponse(responses=responses)


def evaluate_openai_response(data: OpenAIResponse) -> OpenAIEvaluatedResponse:
    """
    Sends all summaries to OpenAI for evaluation and returns the selected index.
    The model must return only the summary number.
    """
    if data is None:
        raise EvaluationError("OpenAI response data cannot be None.")

    if not isinstance(data.responses, list):
        raise EvaluationError("data.responses must be a list of summaries.")

    if not data.responses:
        raise EvaluationError("data.responses cannot be empty.")

    for i, summary in enumerate(data.responses, start=1):
        if not isinstance(summary, str) or not summary.strip():
            raise EvaluationError(f"Summary {i} is invalid or empty.")

    if not isinstance(evaluation_prompt_beginning, str) or not evaluation_prompt_beginning.strip():
        raise EvaluationError("evaluation_prompt_beginning is missing or empty.")

    if not isinstance(evaluation_prompt_ending, str) or not evaluation_prompt_ending.strip():
        raise EvaluationError("evaluation_prompt_ending is missing or empty.")

    eval_prompt = evaluation_prompt_beginning.strip() + "\n\n"

    for i, summary in enumerate(data.responses, start=1):
        eval_prompt += f"Summary {i}:\n{summary.strip()}\n\n"

    eval_prompt += evaluation_prompt_ending.strip()

    client = _get_openai_client()

    try:
        evaluation = client.responses.create(
            model="gpt-4.1-mini",
            input=eval_prompt,
        )
    except Exception as e:
        raise EvaluationError(
            f"Failed to get evaluation response from OpenAI: {str(e)}"
        ) from e

    evaluation_text = getattr(evaluation, "output_text", None)

    if not isinstance(evaluation_text, str):
        raise EvaluationError("Evaluation output is missing or not a string.")

    evaluation_text = evaluation_text.strip()

    if not evaluation_text:
        raise EvaluationError("Evaluation output is empty.")

    if not evaluation_text.isdigit():
        raise EvaluationError(
            f"Invalid evaluation output: '{evaluation_text}'. Expected only a number."
        )

    analysis_result = int(evaluation_text)

    if analysis_result < 1 or analysis_result > len(data.responses):
        raise EvaluationError(
            f"Evaluation output out of range: {analysis_result}. "
            f"Expected a number between 1 and {len(data.responses)}."
        )

    return OpenAIEvaluatedResponse(analysis_result=analysis_result)


def final_clean_up(
    evaluation: OpenAIEvaluatedResponse,
    data: OpenAIResponse,
) -> OpenAIFinalResult:
    """
    Selects the winning summary using the evaluator's chosen index.
    """
    if evaluation is None:
        raise FinalCleanupError("Evaluation result cannot be None.")

    if data is None:
        raise FinalCleanupError("Response data cannot be None.")

    if not isinstance(evaluation.analysis_result, int):
        raise FinalCleanupError("analysis_result must be an integer.")

    if not isinstance(data.responses, list):
        raise FinalCleanupError("data.responses must be a list of summaries.")

    if not data.responses:
        raise FinalCleanupError("data.responses cannot be empty.")

    for i, summary in enumerate(data.responses, start=1):
        if not isinstance(summary, str) or not summary.strip():
            raise FinalCleanupError(f"Summary {i} is invalid or empty.")

    index = evaluation.analysis_result - 1

    if index < 0 or index >= len(data.responses):
        raise FinalCleanupError(
            f"Invalid summary index: {evaluation.analysis_result}. "
            f"Expected a number between 1 and {len(data.responses)}."
        )

    selected_text = data.responses[index].strip()

    if not selected_text:
        raise FinalCleanupError("Selected summary is empty.")

    return OpenAIFinalResult(final_text=selected_text)