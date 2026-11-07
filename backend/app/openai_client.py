import os
from json import JSONDecodeError
from typing import TypeVar

from openai import APITimeoutError, OpenAI, OpenAIError
from pydantic import BaseModel, ValidationError

from .schemas import CandidateFinding, FollowUpResult, ModelFindings

ModelResult = TypeVar("ModelResult", bound=BaseModel)


class ModelConfigurationError(Exception):
    pass


class ModelTimeout(Exception):
    pass


class ModelResponseError(Exception):
    pass


def generate_findings(instructions: str, user_input: str) -> list[CandidateFinding]:
    return _generate_structured(instructions, user_input, ModelFindings).findings


def generate_follow_up(instructions: str, user_input: str) -> FollowUpResult:
    return _generate_structured(instructions, user_input, FollowUpResult)


def _generate_structured(
    instructions: str, user_input: str, text_format: type[ModelResult]
) -> ModelResult:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    model = os.getenv("OPENAI_MODEL", "gpt-6.1-sol").strip()
    effort = os.getenv("OPENAI_REASONING_EFFORT", "high").strip()
    if not api_key or not model or effort not in {"low", "medium", "high", "xhigh", "max"}:
        raise ModelConfigurationError

    try:
        with OpenAI(api_key=api_key, timeout=60.0, max_retries=0) as client:
            response = client.responses.parse(
                model=model,
                instructions=instructions,
                input=user_input,
                reasoning={"effort": effort},
                text_format=text_format,
                store=False,
                max_output_tokens=8192,
            )
    except APITimeoutError:
        raise ModelTimeout from None
    except (OpenAIError, ValidationError, JSONDecodeError):
        raise ModelResponseError from None

    parsed = response.output_parsed
    if response.status != "completed" or parsed is None:
        raise ModelResponseError
    return parsed
