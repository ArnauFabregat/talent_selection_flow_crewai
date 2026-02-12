# optional: Pydantic schemas for outputs (rankings)
from pydantic import BaseModel, Field
from typing import List


class RetrievalItem(BaseModel):
    job_id: str = Field(description="Identifier of the retrieved job posting.")
    similarity: float = Field(description="ChromaDB similarity score for this job.")


class RetrievalResult(BaseModel):
    top_k: int = Field(description="Number of job matches returned.")
    results: List[RetrievalItem] = Field(
        description="List of retrieved jobs with their similarity scores."
    )
