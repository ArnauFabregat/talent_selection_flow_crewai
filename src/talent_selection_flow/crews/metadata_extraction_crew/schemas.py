"""
Metadata Extraction Schemas.

This module defines the Pydantic models used to structure extracted information
from raw text. These schemas act as the blueprint for the MetadataExtractionCrews
and ensure compatibility with ChromaDB's flat metadata requirements.
"""

from pydantic import BaseModel

from src.talent_selection_flow.crews.metadata_extraction_crew.enums import (
    EducationLevel,
    EmploymentType,
    ExperienceLevel,
)


class BaseProfile(BaseModel):
    """
    Common foundational metadata structure.

    This base class forces normalization across different document types.
    To maintain compatibility with ChromaDB, complex lists (like skills)
    are flattened into comma-separated strings.

    Attributes:
        skills (str | None): Flattened list of technical/soft skills.
        industries (str | None): Relevant sectors (e.g., 'Fintech, Healthcare').
        experience_level (ExperienceLevel): Enum-validated seniority.
        country (str | None): Geographic location for regional filtering.
        summary (str): A concise AI-generated blurb of the document.
    """

    skills: str | None = None
    industries: str | None = None
    experience_level: ExperienceLevel
    country: str | None = None
    summary: str


class CVMetadata(BaseProfile):
    """
    Structured representation of a Candidate's CV.

    Extends the base profile with candidate-specific academic and
    linguistic attributes.

    Attributes:
        education_level (EducationLevel): Highest degree obtained.
        languages (str | None): Flattened list of spoken languages.
    """

    education_level: EducationLevel
    languages: str | None = None


class JobMetadata(BaseProfile):
    """
    Structured representation of a Job Posting.

    Extends the base profile with operational details required by
    hiring managers and recruiters.

    Attributes:
        title (str): The official name of the position.
        city (str | None): Specific city location (if applicable).
        employment_type (EmploymentType): Full-time, Contract, etc.
        responsibilities (str | None): Flattened list of core job duties.
    """

    title: str
    city: str | None = None
    employment_type: EmploymentType
    responsibilities: str | None = None
