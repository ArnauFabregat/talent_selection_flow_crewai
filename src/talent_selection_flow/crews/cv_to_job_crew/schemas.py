from pydantic import BaseModel, Field
from typing import Dict

from src.talent_selection_flow.crews.schemas import GapAnalysis, Questions


class GapAnalysisOutput(BaseModel):
    docs: Dict[str, GapAnalysis] = Field(
        description="Mapping of job_id to its gap analysis result."
    )


class InterviewQuestionsOutput(BaseModel):
    docs: Dict[str, Questions] = Field(description="Mapping of job_id to its interview question set.")
