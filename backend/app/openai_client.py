import os
from json import JSONDecodeError

from openai import APITimeoutError, OpenAI, OpenAIError
from pydantic import ValidationError

from .schemas import CandidateFinding, ModelFindings


class ModelConfigurationError(Exception):
    pass


class ModelTimeout(Exception):
    pass


class ModelResponseError(Exception):
    pass


def generate_findings(instructions: str, user_input: str) -> list[CandidateFinding]:
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
                text_format=ModelFindings,
                store=False,
                max_output_tokens=8192,
            )
    except APITimeoutError:
        raise ModelTimeout from None
    except (OpenAIError, ValidationError, JSONDecodeError):
        raise ModelResponseError from None

    if response.status != "completed" or response.output_parsed is None:
        raise ModelResponseError
    return response.output_parsed.findings
