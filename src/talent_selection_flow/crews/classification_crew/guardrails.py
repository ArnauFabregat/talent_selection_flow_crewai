from typing import Any, Tuple
from crewai import TaskOutput

from src.talent_selection_flow.crews.classification_crew.enums import DocumentType
from src.utils.logger import logger


def validate_classifier_output(result: TaskOutput) -> Tuple[bool, Any]:
    """Validates str format and enum values in one pass."""
    logger.debug(f"Guardrail input: '{result.raw}'")
    # 1. Sanitize: Strip whitespace AND common wrapping characters like quotes/periods
    result_str = result.raw.strip().strip('."\'`')

    if not result_str or ' ' in result_str:
        logger.warning("Guardrail `validate_classifier_output` triggered: invalid string format")
        return (False, "Invalid string format, must be a single word. Please fix")

    # 2. Validate enums
    if result_str not in DocumentType._value2member_map_:
        logger.warning(f"Guardrail `validate_classifier_output` triggered: invalid output field")
        return (False, f"Invalid field. Output must be one of {'/'.join(DocumentType)}")

    return (True, result_str)
