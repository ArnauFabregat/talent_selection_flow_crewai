from pydantic import BaseModel, Field

from src.talent_selection_flow.crews.schemas import GapAnalysis, Questions


class GapAnalysisOutput(BaseModel):
    docs: dict[str, GapAnalysis] = Field(description="Mapping of cv_id to its gap analysis result.")


class InterviewQuestionsOutput(BaseModel):
    docs: dict[str, Questions] = Field(description="Mapping of cv_id to its interview question set.")
