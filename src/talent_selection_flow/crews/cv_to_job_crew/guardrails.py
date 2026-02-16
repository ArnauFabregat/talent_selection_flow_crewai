import json
from typing import Any, Tuple, List
from crewai import TaskOutput

from src.utils.logger import logger
from src.talent_selection_flow.crews.cv_to_job_crew.schemas import JobGapAnalysis


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
    if "jobs" not in data or not isinstance(data["jobs"], dict):
        logger.warning("Guardrail `validate_gapanalysisoutput_schema` triggered: missing or invalid 'jobs' key")
        return (False, "Missing or invalid 'jobs' key. Expected: {'jobs': {'ID': {...}}}")

    # 2. Deep Dive into each Job entry
    for jid, content in data["jobs"].items():
        try:
            # Use Pydantic to validate the inner object
            # This checks types, missing fields, and extra fields in one go
            JobGapAnalysis.model_validate(content)
        except Exception as e:
            # Pydantic's error messages are very descriptive for LLMs
            errors.append(f"Job ID '{jid}' validation error: {str(e)}")

    # 3. Return
    if errors:
        logger.warning(f"Guardrail `validate_gapanalysisoutput_schema` triggered: invalid job entries.")
        feedback: str = "Guardrail `validate_gapanalysisoutput_schema` validation failed:\n- " + "\n- ".join(errors)
        logger.debug(feedback)
        return (False, feedback)

    return (True, json.dumps(data))
