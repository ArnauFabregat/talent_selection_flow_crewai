from pydantic import BaseModel
from typing import Optional

from src.talent_selection_flow.crews.metadata_extraction_crew.enums import (
    ExperienceLevel, EducationLevel, EmploymentType,
)


class BaseProfile(BaseModel):
    """
    Base profile structure shared by both CVs and job postings.

    All fields must be strings due to ChromaDB metadata constraints.
    Multi-value fields (skills, industries...) should be represented as
    comma-separated strings.

    Fields:
        skills (str): Comma-separated list of skills.
        industries (str): Comma-separated list of relevant industries.
        experience_level (ExperienceLevel): Normalized seniority level.
        country (str, optional): Candidate's country or job location.
        summary (str): Short document summary.
    """

    skills: Optional[str] = None
    industries: Optional[str] = None
    experience_level: ExperienceLevel
    country: Optional[str] = None
    summary: str


class CVMetadata(BaseProfile):
    """
    Metadata extracted from candidate CVs.

    Fields:
        education_level (EducationLevel): Highest education level inferred.
        languages (str, optional): Comma-separated language list.
    """

    education_level: EducationLevel
    languages: Optional[str] = None


class JobMetadata(BaseProfile):
    """
    Metadata extracted from job postings.

    Fields:
        title (str): Job title.
        city (str, optional): Job location.
        employment_type (EmploymentType): Full-time, part-time, contract, etc.
        responsibilities (str, optional): Comma-separated job responsibilities.
    """

    title: str
    city: Optional[str] = None
    employment_type: EmploymentType
    responsibilities: Optional[str] = None
