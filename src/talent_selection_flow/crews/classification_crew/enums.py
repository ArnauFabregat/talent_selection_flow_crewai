"""
Classification Enums for Talent Selection.

This module defines the primary document categories used by the
ClassificationCrew to route the logic of the TalentSelectionFlow.
"""

from enum import StrEnum


class DocumentType(StrEnum):
    """
    Categorical classification for incoming user documents.

    Used by the initial routing step to determine which metadata extraction
    crew and vector database collection to utilize.

    Attributes:
        CV: Represents a candidate's Curriculum Vitae or Resume.
        JOB: Represents a Job Description or Role Requirement document.
        OTHER: Represents invalid or unrecognized input that does not
            fit the recruitment evaluation scope.
    """

    CV = "cv"
    JOB = "job"
    OTHER = "other"
