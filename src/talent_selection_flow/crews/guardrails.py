import json
from typing import Any, Tuple, List
from crewai import TaskOutput

from src.utils.logger import logger
from src.talent_selection_flow.crews.cv_to_job_crew.schemas import GapAnalysis, Questions


def validate_gapanalysisoutput_schema(result: TaskOutput) -> Tuple[bool, Any]:
    """Validates JSON format, schema, and enum values in one pass."""
    logger.debug(f"Guardrail input:\n{result.raw}")
    # 1. Validate JSON
    try:
        data = json.loads(result.raw)
    except json.JSONDecodeError:
        logger.warning("Guardrail `validate_gapanalysisoutput_schema` triggered: invalid JSON format")
        return (False, "Invalid JSON format. Please fix")

    errors: List[str] = []

    # 1. Validate first nesting level
    if "docs" not in data or not isinstance(data["docs"], dict):
        logger.warning("Guardrail `validate_gapanalysisoutput_schema` triggered: missing or invalid 'docs' key")
        return (False, "Missing or invalid 'docs' key. Expected: {'docs': {'ID': {...}}}")

    # 2. Deep Dive into each doc entry
    for doc_id, content in data["docs"].items():
        try:
            # Use Pydantic to validate the inner object
            # This checks types, missing fields, and extra fields in one go
            GapAnalysis.model_validate(content)
        except Exception as e:
            # Pydantic's error messages are very descriptive for LLMs
            errors.append(f"Doc ID '{doc_id}' validation error: {str(e)}")

    # 3. Return
    if errors:
        logger.warning(f"Guardrail `validate_gapanalysisoutput_schema` triggered: invalid doc entries.")
        feedback: str = "Guardrail `validate_gapanalysisoutput_schema` validation failed:\n- " + "\n- ".join(errors)
        logger.debug(feedback)
        return (False, feedback)

    return (True, json.dumps(data))


def validate_interviewquestionsoutput_schema(result: TaskOutput) -> Tuple[bool, Any]:
    """Validates JSON format, schema, and enum values in one pass."""
    logger.debug(f"Guardrail input:\n{result.raw}")
    # 1. Validate JSON
    try:
        data = json.loads(result.raw)
    except json.JSONDecodeError:
        logger.warning("Guardrail `validate_interviewquestionsoutput_schema` triggered: invalid JSON format")
        return (False, "Invalid JSON format. Please fix")

    errors: List[str] = []

    # 1. Validate first nesting level
    if "docs" not in data or not isinstance(data["docs"], dict):
        logger.warning("Guardrail `validate_interviewquestionsoutput_schema` triggered: missing or invalid 'docs' key")
        return (False, "Missing or invalid 'docs' key. Expected: {'docs': {'ID': {...}}}")

    # 2. Deep Dive into each doc entry
    for doc_id, content in data["docs"].items():
        try:
            # Use Pydantic to validate the inner object
            # This checks types, missing fields, and extra fields in one go
            Questions.model_validate(content)
        except Exception as e:
            # Pydantic's error messages are very descriptive for LLMs
            errors.append(f"Doc ID '{doc_id}' validation error: {str(e)}")

    # 3. Return
    if errors:
        logger.warning(f"Guardrail `validate_interviewquestionsoutput_schema` triggered: invalid doc entries.")
        feedback: str = "Guardrail `validate_interviewquestionsoutput_schema` validation failed:\n- " + "\n- ".join(errors)
        logger.debug(feedback)
        return (False, feedback)

    return (True, json.dumps(data))
