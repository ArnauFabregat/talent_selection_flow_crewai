# optional: Pydantic schemas for outputs (rankings)
from typing import List
from pydantic import BaseModel, Field


class JobMatch(BaseModel):
    job_id: str = Field(..., description="Unique id for job posting (Chroma document id)")
    title: str = Field(..., description="Job title (from metadata or inferred)")
    company: str = Field(..., description="Company name (from metadata if present)")
    location: str = Field(..., description="Location (from metadata if present)")
    similarity: float = Field(..., ge=0.0, le=1.0, description="Similarity score 0..1")
    snippet: str = Field(..., description="Short snippet of job description")
    full_text: str = Field(..., description="Full job posting text")


class RetrievalResult(BaseModel):
    query_summary: str
    top_k: int
    matches: List[JobMatch]
