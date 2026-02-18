"""
Metadata Extraction Enums.

This module provides strictly defined categories for education,
experience, and employment types. These enums are used by the
MetadataExtractor crews to normalize unstructured text into
standardized database attributes.
"""

from enum import StrEnum


class EducationLevel(StrEnum):
    """
    Standardized academic achievement levels.

    Used to filter candidate eligibility or job requirements.
    """

    HIGHSCHOOL = "highschool"
    BACHELOR = "bachelor"
    MASTER = "master"
    PHD = "phd"
    OTHER = "other"
    UNKNOWN = "unknown"


class ExperienceLevel(StrEnum):
    """
    Normalized seniority levels.

    Helps in the 'Seniority Questions' generation phase by
    aligning candidate years of experience with role expectations.
    """

    INTERN = "intern"
    ENTRY = "entry"
    INTERMEDIATE = "intermediate"
    SENIOR = "senior"
    OTHER = "other"
    UNKNOWN = "unknown"


class EmploymentType(StrEnum):
    """
    Contractual nature of the role.

    Used to match candidate preferences with job availability.
    """

    FULL_TIME = "full-time"
    PART_TIME = "part-time"
    CONTRACT = "contract"
    FREELANCE = "freelance"
    OTHER = "other"
    UNKNOWN = "unknown"
