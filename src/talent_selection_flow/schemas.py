"""
State Management Module for Talent Selection.

This module defines the schema for the shared state used throughout the
TalentSelectionFlow. It leverages Pydantic for data validation and
consistency across multiple asynchronous steps.
"""

from typing import Any

from pydantic import BaseModel

from src.talent_selection_flow.crews.classification_crew.enums import DocumentType


class TalentState(BaseModel):
    """
    Represents the internal state of a talent evaluation process.

    This state object is passed between different tasks in the flow,
    storing raw user inputs, classified types, retrieved documents from
    ChromaDB, and the final evaluation report.

    Attributes:
        raw_input (str): The original text or markdown content provided by
            the user (e.g., a resume or job description).
        input_type (DocumentType): The categorical classification of the
            input (e.g., CV, JOB_DESCRIPTION, or OTHER).
        metadata (dict[str, Any]): Extracted structured data such as
            candidate name, skills, or job title.
        related_docs (dict[str, Any]): Semantic search results from
            the vector database (e.g., matching jobs for a CV).
        process_crew (Any): A reference to the specific crew instance
            or execution context currently handling the state.
    """

    raw_input: str = ""
    input_type: DocumentType = DocumentType.OTHER
    metadata: dict[str, Any] = {}
    related_docs: dict[str, Any] = {}
    process_crew: Any = None
