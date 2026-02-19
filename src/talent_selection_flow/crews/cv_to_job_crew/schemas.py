"""
Container Schemas for Bulk Analysis.

This module defines the high-level output structures used by the analysis crews.
These schemas wrap individual GapAnalysis and Questions models into dictionaries
keyed by document IDs, allowing for structured multi-document reporting.
"""

from pydantic import BaseModel, Field

from src.talent_selection_flow.crews.schemas import GapAnalysis, Questions


class GapAnalysisOutput(BaseModel):
    """
    A collection of gap analyses for multiple document matches.

    This model acts as a registry, mapping specific database IDs (Job IDs or CV IDs)
    to their respective technical gap evaluations.

    Attributes:
        docs (dict[str, GapAnalysis]): A dictionary where keys are unique identifiers
            from ChromaDB and values are GapAnalysis instances.
    """

    docs: dict[str, GapAnalysis] = Field(description="Mapping of job_id to its gap analysis result.")


class InterviewQuestionsOutput(BaseModel):
    """
    A collection of interview question sets for multiple document matches.

    This model organizes tailored interview strategies for all retrieved matches,
    ensuring that the hiring manager receives specific guidance for every
    candidate or job analyzed.

    Attributes:
        docs (dict[str, Questions]): A dictionary where keys are unique identifiers
            from ChromaDB and values are Questions instances.
    """

    docs: dict[str, Questions] = Field(description="Mapping of job_id to its interview question set.")
