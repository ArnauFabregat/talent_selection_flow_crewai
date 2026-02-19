"""
Metadata Validation Guardrails.

This module provides specialized validation functions for CV and Job metadata.
Beyond basic JSON schema checks, it enforces strict enum compliance and
standardizes geographic data using the ISO 3166-1 alpha-2 standard via `pycountry`.
"""

import json
from typing import Any

from crewai import TaskOutput
from pycountry import countries

from src.talent_selection_flow.crews.metadata_extraction_crew.enums import (
    EducationLevel,
    EmploymentType,
    ExperienceLevel,
)
from src.utils.logger import logger


def validate_cvmetadata_schema(result: TaskOutput) -> tuple[bool, Any]:
    """
    Validates the structure and semantic values of extracted CV metadata.

    Ensures that the LLM output can be parsed as JSON and that critical
    categorical fields (education, experience, and country) contain
    recognized values.

    Parameters
    ----------
    result : TaskOutput
        The raw output from the CV extraction agent.

    Returns
    -------
    tuple[bool, Any]
        (True, sanitized_json_string) if valid; (False, error_feedback) otherwise.
    """
    logger.debug(f"Guardrail input:\n{result.raw}")
    # 1. Validate JSON
    try:
        data = json.loads(result.raw)
    except json.JSONDecodeError:
        logger.warning("Guardrail `validate_cvmetadata_schema` triggered: invalid JSON format")
        return (False, "Invalid JSON format. Please fix")

    fields: list[str] = []
    errors: list[str] = []

    # 2. Validate enums
    if data.get("education_level") not in EducationLevel._value2member_map_:
        fields.append("education_level")
        errors.append(f"education_level must be one of {'/'.join(EducationLevel)}")

    if data.get("experience_level") not in ExperienceLevel._value2member_map_:
        fields.append("experience_level")
        errors.append(f"experience_level must be one of {'/'.join(ExperienceLevel)}")

    # 3. Validate country (ISO Alpha-2 enforcement)
    if data.get("country"):
        if countries.get(alpha_2=data.get("country")) is None:
            fields.append("country")
            errors.append(
                f"`{data.get('country')}` is not valid. Must be a country and in ISO Alpha-2 code (e.g., 'US', 'ES')"
            )

    # 4. Return
    if errors:
        logger.warning(f"Guardrail `validate_cvmetadata_schema` triggered: invalid fields for `{', '.join(fields)}`")
        return (False, f"Invalid field. Fix these:\n{'; '.join(errors)}")

    return (True, json.dumps(data))


def validate_jobmetadata_schema(result: TaskOutput) -> tuple[bool, Any]:
    """
    Validates the structure and semantic values of extracted Job metadata.

    Ensures alignment between the job description analysis and the
    required data schema for hiring processes.

    Parameters
    ----------
    result : TaskOutput
        The raw output from the Job extraction agent.

    Returns
    -------
    tuple[bool, Any]
        (True, sanitized_json_string) if valid; (False, error_feedback) otherwise.
    """
    logger.debug(f"Guardrail input:\n{result.raw}")
    # 1. Validate JSON
    try:
        data = json.loads(result.raw)
    except json.JSONDecodeError:
        logger.warning("Guardrail `validate_jobmetadata_schema` triggered: invalid JSON format")
        return (False, "Invalid JSON format. Please fix")

    fields: list[str] = []
    errors: list[str] = []

    # 2. Validate enums
    if data.get("employment_type") not in EmploymentType._value2member_map_:
        fields.append("employment_type")
        errors.append(f"employment_type must be one of {'/'.join(EmploymentType)}")

    if data.get("experience_level") not in ExperienceLevel._value2member_map_:
        fields.append("experience_level")
        errors.append(f"experience_level must be one of {'/'.join(ExperienceLevel)}")

    # 3. Validate country (ISO Alpha-2 enforcement)
    if data.get("country"):
        if countries.get(alpha_2=data.get("country")) is None:
            fields.append("country")
            errors.append(
                f"`{data.get('country')}` is not valid. Must be a country and in ISO Alpha-2 code (e.g., 'US', 'ES')"
            )

    # 4. Return
    if errors:
        logger.warning(f"Guardrail `validate_jobmetadata_schema` triggered: invalid fields for `{', '.join(fields)}`")
        return (False, f"Invalid field. Fix these:\n{'; '.join(errors)}")

    return (True, json.dumps(data))
