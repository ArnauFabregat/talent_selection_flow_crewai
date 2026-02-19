"""
Classification Guardrail Module.

This module provides validation logic to ensure that the initial document
classifier returns a clean, single-word string that strictly matches the
predefined DocumentType categories.
"""

from typing import Any

from crewai import TaskOutput

from src.talent_selection_flow.crews.classification_crew.enums import DocumentType
from src.utils.logger import logger


def validate_classifier_output(result: TaskOutput) -> tuple[bool, Any]:
    """
    Validates and sanitizes the output of the Document Classification task.

    This guardrail performs a 'soft' clean of the LLM response by removing
    common punctuation and whitespace, then verifies the result against
    the allowed DocumentType enum values.

    Parameters
    ----------
    result : TaskOutput
        The raw output from the classification agent, expected to be a
        single word (e.g., 'cv', 'job', or 'other').

    Returns
    -------
    tuple[bool, Any]
        A tuple containing:
        - bool: Success flag (True if output is valid).
        - Any: The sanitized string on success, or an error message
          string for the LLM to use for self-correction on failure.
    """
    logger.debug(f"Guardrail input: '{result.raw}'")

    # 1. Sanitize: Strip whitespace AND common wrapping characters like quotes/periods
    # This handles LLM quirks like returning '"cv".' instead of 'cv'
    result_str = result.raw.strip().strip(".\"'`")

    if not result_str or " " in result_str:
        logger.warning("Guardrail `validate_classifier_output` triggered: invalid string format")
        return (False, "Invalid string format, must be a single word. Please fix")

    # 2. Validate enums
    # Uses the internal mapping to check if the string matches an enum value
    if result_str not in DocumentType._value2member_map_:
        logger.warning("Guardrail `validate_classifier_output` triggered: invalid output field")
        return (False, f"Invalid field. Output must be one of {'/'.join(DocumentType)}")

    return (True, result_str)
