"""
Task Output Guardrails Module.

This module provides validation functions (guardrails) designed to verify that
AI agents return structured data matching the expected JSON schema. It
performs multi-level validation: JSON syntax, top-level key existence,
and nested object schema via Pydantic.
"""

import json
from typing import Any

from crewai import TaskOutput

from src.talent_selection_flow.crews.cv_to_job_crew.schemas import GapAnalysis, Questions
from src.utils.logger import logger


def validate_gapanalysisoutput_schema(result: TaskOutput) -> tuple[bool, Any]:
    """
    Validates the JSON format and schema for Gap Analysis outputs.

    This guardrail ensures the LLM output follows a nested dictionary structure:
    {'docs': {'DOC_ID': GapAnalysisModel}}. It uses Pydantic to provide
    detailed error feedback if technical validation fails.

    Parameters
    ----------
    result : TaskOutput
        The raw output object from the CrewAI task containing the generated string.

    Returns
    -------
    tuple[bool, Any]
        A tuple where the first element is a success flag (bool).
        The second element is either the cleaned JSON string (on success)
        or descriptive error feedback (on failure).
    """
    logger.debug(f"Guardrail input:\n{result.raw}")
    # 1. Validate JSON
    try:
        data = json.loads(result.raw)
    except json.JSONDecodeError:
        logger.warning("Guardrail `validate_gapanalysisoutput_schema` triggered: invalid JSON format")
        return (False, "Invalid JSON format. Please fix")

    errors: list[str] = []

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
        logger.warning("Guardrail `validate_gapanalysisoutput_schema` triggered: invalid doc entries.")
        feedback: str = "Guardrail `validate_gapanalysisoutput_schema` validation failed:\n- " + "\n- ".join(errors)
        logger.debug(feedback)
        return (False, feedback)

    return (True, json.dumps(data))


def validate_interviewquestionsoutput_schema(result: TaskOutput) -> tuple[bool, Any]:
    """
    Validates the JSON format and schema for Interview Questions outputs.

    Similar to the gap analysis guardrail, this ensures the LLM correctly
    attributes sets of interview questions to specific document IDs
    under a top-level 'docs' key.

    Parameters
    ----------
    result : TaskOutput
        The raw output object from the CrewAI task.

    Returns
    -------
    tuple[bool, Any]
        A success/fail tuple where failure includes granular Pydantic
        validation errors to guide LLM re-generation.
    """
    logger.debug(f"Guardrail input:\n{result.raw}")
    # 1. Validate JSON
    try:
        data = json.loads(result.raw)
    except json.JSONDecodeError:
        logger.warning("Guardrail `validate_interviewquestionsoutput_schema` triggered: invalid JSON format")
        return (False, "Invalid JSON format. Please fix")

    errors: list[str] = []

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
        logger.warning("Guardrail `validate_interviewquestionsoutput_schema` triggered: invalid doc entries.")
        feedback: str = "Guardrail `validate_interviewquestionsoutput_schema` validation failed:\n- " + "\n- ".join(
            errors
        )
        logger.debug(feedback)
        return (False, feedback)

    return (True, json.dumps(data))
