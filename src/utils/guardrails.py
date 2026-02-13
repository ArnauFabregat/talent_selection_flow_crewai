import json
from typing import Any, Tuple, List
from crewai import TaskOutput
from pycountry import countries

from src.db_ingestion.enums import ExperienceLevel, EducationLevel, EmploymentType
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
    data = json.loads(result.raw)
    fields: List[str] = []
    errors: List[str] = []

    if data.get("education_level") not in EducationLevel._value2member_map_:
        fields.append("education_level")
        errors.append(f"education_level must be one of {"/".join(EducationLevel)}")
    if data.get("experience_level") not in ExperienceLevel._value2member_map_:
        fields.append("experience_level")
        errors.append(f"experience_level must be one of {"/".join(ExperienceLevel)}")
    if data.get("country"):
        if countries.get(alpha_2=data.get("country")) is None:
            fields.append("country")
            errors.append("country must be in ISO Alpha-2 code")
    if errors:
        logger.warning(f"Guardrail `validate_cvmetadata_schema` triggered for fields: {', '.join(fields)}")
        return (False, f"Fix these:\n{'; '.join(errors)}")
    return (True, result)


def validate_jobmetadata_schema(result: TaskOutput) -> Tuple[bool, Any]:
    """
    Should go after validate_json_format guardrail
    """
    data = json.loads(result.raw)
    fields: List[str] = []
    errors: List[str] = []

    if data.get("employment_type") not in EmploymentType._value2member_map_:
        fields.append("employment_type")
        errors.append(f"employment_type must be one of {"/".join(EmploymentType)}")
    if data.get("experience_level") not in ExperienceLevel._value2member_map_:
        fields.append("experience_level")
        errors.append(f"experience_level must be one of {"/".join(ExperienceLevel)}")
    if data.get("country"):
        if countries.get(alpha_2=data.get("country")) is None:
            fields.append("country")
            errors.append("country must be in ISO Alpha-2 code")
    if errors:
        logger.warning(f"Guardrail `validate_jobmetadata_schema` triggered for fields: {', '.join(fields)}")
        return (False, f"Fix these:\n{'; '.join(errors)}")
    return (True, result)
