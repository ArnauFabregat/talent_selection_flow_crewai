import json
from typing import Any, Tuple, List
from crewai import TaskOutput
from pycountry import countries

from src.db_ingestion.metadata_extraction_crew.enums import ExperienceLevel, EducationLevel, EmploymentType
from src.utils.logger import logger


def validate_cvmetadata_schema(result: TaskOutput) -> Tuple[bool, Any]:
    """Validates JSON format, schema, and enum values in one pass."""
    logger.debug(f"Guardrail input:\n{result.raw}")
    # 1. Validate JSON
    try:
        data = json.loads(result.raw)
    except json.JSONDecodeError:
        logger.warning("Guardrail `validate_cvmetadata_schema` triggered: invalid JSON format")
        return (False, "Invalid JSON format. Please fix")

    fields: List[str] = []
    errors: List[str] = []

    # 2. Validate enums
    if data.get("education_level") not in EducationLevel._value2member_map_:
        fields.append("education_level")
        errors.append(f"education_level must be one of {'/'.join(EducationLevel)}")

    if data.get("experience_level") not in ExperienceLevel._value2member_map_:
        fields.append("experience_level")
        errors.append(f"experience_level must be one of {'/'.join(ExperienceLevel)}")

    # 3. Validate country
    if data.get("country"):
        if countries.get(alpha_2=data.get("country")) is None:
            fields.append("country")
            errors.append("country must be in ISO Alpha-2 code")

    # 4. Return
    if errors:
        logger.warning(f"Guardrail `validate_cvmetadata_schema` triggered: invalid fields for `{', '.join(fields)}`")
        return (False, f"Invalid field. Fix these:\n{'; '.join(errors)}")

    return (True, json.dumps(data))


def validate_jobmetadata_schema(result: TaskOutput) -> Tuple[bool, Any]:
    """Validates JSON format, schema, and enum values in one pass."""
    logger.debug(f"Guardrail input:\n{result.raw}")
    # 1. Validate JSON
    try:
        data = json.loads(result.raw)
    except json.JSONDecodeError:
        logger.warning("Guardrail `validate_jobmetadata_schema` triggered: invalid JSON format")
        return (False, "Invalid JSON format. Please fix")

    fields: List[str] = []
    errors: List[str] = []

    # 2. Validate enums
    if data.get("employment_type") not in EmploymentType._value2member_map_:
        fields.append("employment_type")
        errors.append(f"employment_type must be one of {'/'.join(EmploymentType)}")

    if data.get("experience_level") not in ExperienceLevel._value2member_map_:
        fields.append("experience_level")
        errors.append(f"experience_level must be one of {'/'.join(ExperienceLevel)}")

    # 3. Validate country
    if data.get("country"):
        if countries.get(alpha_2=data.get("country")) is None:
            fields.append("country")
            errors.append("country must be in ISO Alpha-2 code")

    # 4. Return
    if errors:
        logger.warning(f"Guardrail `validate_jobmetadata_schema` triggered: invalid fields for `{', '.join(fields)}`")
        return (False, f"Invalid field. Fix these:\n{'; '.join(errors)}")

    return (True, json.dumps(data))
