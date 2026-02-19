"""
Job-to-CV Container Schemas.

This module defines the high-level output structures for crews analyzing
candidates against a specific job description. It wraps individual
analysis models into registries keyed by candidate IDs.
"""

from pydantic import BaseModel, Field

from src.talent_selection_flow.crews.schemas import GapAnalysis, Questions


class GapAnalysisOutput(BaseModel):
    """
    A registry of gap analyses for a set of candidates.

    This model aggregates technical audits for multiple CVs, allowing
    the system to compare several candidates against one job role.

    Attributes:
        docs (dict[str, GapAnalysis]): A dictionary where keys are candidate
            IDs (cv_id) and values are GapAnalysis objects containing
            matched and missing skills.
    """

    docs: dict[str, GapAnalysis] = Field(description="Mapping of cv_id to its gap analysis result.")


class InterviewQuestionsOutput(BaseModel):
    """
    A registry of interview strategies for a set of candidates.

    Organizes custom interview questions and expected responses for
    every candidate evaluated during the job-to-cv matching process.

    Attributes:
        docs (dict[str, Questions]): A dictionary where keys are candidate
            IDs (cv_id) and values are Questions objects.
    """

    docs: dict[str, Questions] = Field(description="Mapping of cv_id to its interview question set.")
