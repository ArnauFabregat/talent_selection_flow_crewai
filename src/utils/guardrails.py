import json
from typing import Any, Tuple
from crewai import TaskOutput

from src.utils.logger import logger


def validate_json_output(result: TaskOutput) -> Tuple[bool, Any]:
    """Validate and parse JSON output."""
    try:
        # Try to parse as JSON
        data = json.loads(result.raw)
        return (True, data)
    except json.JSONDecodeError:
        return (False, "Invalid JSON format")


def validate_employment_type(result: TaskOutput) -> Tuple[bool, Any]:
    valid_types = ['full-time', 'part-time', 'contract', 'freelance', 'other']
    if not any(t in result.raw for t in valid_types):
        logger.warning("Guardrail triggered: validate_employment_type")
        return (False, "employment_type must be one of: full-time, part-time, contract, freelance, other. Please fix.")
    return (True, result.raw)
