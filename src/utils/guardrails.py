import json
from typing import Any, Tuple, List
from crewai import TaskOutput

from src.utils.logger import logger


def validate_json_output(result: TaskOutput) -> Tuple[bool, Any]:
    try:
        json.loads(result.raw)
        return (True, result.raw)
    except json.JSONDecodeError:
        logger.warning("Guardrail triggered: validate_json_output")
        return (False, "Invalid JSON format. Please fix")


def validate_cvmetadata_schema(result: TaskOutput) -> Tuple[bool, Any]:
    """
    Should go after validate_json_format guardrail
    """
    education_levels = ["highschool", "bachelor", "master", "phd", "other", "unknown"]
    experience_levels = ["intern", "entry", "intermediate", "senior", "other", "unknown"]

    data = json.loads(result.raw)
    fields: List[str] = []
    errors: List[str] = []

    if data.get("education_level") not in education_levels:
        fields.append("education_level")
        errors.append("education_level must be one of highschool/bachelor/master/phd/other/unknown")
    if data.get("experience_level") not in experience_levels:
        fields.append("experience_level")
        errors.append("experience_level must be one of intern/entry/intermediate/senior/other/unknown")
    if errors:
        logger.warning(f"Guardrail `validate_cvmetadata_schema` triggered for fields: {', '.join(fields)}")
        return (False, f"Fix these:\n{'; '.join(errors)}")
    return (True, result)


def validate_jobmetadata_schema(result: TaskOutput) -> Tuple[bool, Any]:
    """
    Should go after validate_json_format guardrail
    """
    emplyment_types = ["full-time", "part-time", "contract", "freelance", "other", "unknown"]
    experience_levels = ["intern", "entry", "intermediate", "senior", "other", "unknown"]

    data = json.loads(result.raw)
    fields: List[str] = []
    errors: List[str] = []

    if data.get("employment_type") not in emplyment_types:
        fields.append("employment_type")
        errors.append("employment_type must be one of full-time/part-time/contract/freelance/other/unknown")
    if data.get("experience_level") not in experience_levels:
        fields.append("experience_level")
        errors.append("experience_level must be one of intern/entry/intermediate/senior/other/unknown")
    if errors:
        logger.warning(f"Guardrail `validate_jobmetadata_schema` triggered for fields: {', '.join(fields)}")
        return (False, f"Fix these:\n{'; '.join(errors)}")
    return (True, result)
