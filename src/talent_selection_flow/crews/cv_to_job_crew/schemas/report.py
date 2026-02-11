# optional: report schema/output formatting
from typing import List, Literal
from pydantic import BaseModel, Field


class GapAnalysis(BaseModel):
    job_id: str
    overall_fit_score: int = Field(..., ge=0, le=100)
    matched_skills: List[str] = Field(default_factory=list)
    missing_must_have: List[str] = Field(default_factory=list)
    missing_nice_to_have: List[str] = Field(default_factory=list)
    ambiguities: List[str] = Field(default_factory=list)
    seniority_mismatch: Literal["none", "candidate_overqualified", "candidate_underqualified"] = "none"
    notes: str = ""


class InterviewQuestion(BaseModel):
    type: Literal["matched", "gap", "ambiguity", "seniority"]
    question: str
    right_answer: str = ""


class QuestionSet(BaseModel):
    job_id: str
    questions: List[InterviewQuestion] = Field(default_factory=list)


class FinalReportModel(BaseModel):
    """
    Optional structured report representation.
    In this first iteration, we write Markdown, but you can use this later to generate PDF, etc.
    """
    executive_summary: str
    top_matches: List[str] = Field(default_factory=list)
    analyses: List[GapAnalysis] = Field(default_factory=list)
    question_sets: List[QuestionSet] = Field(default_factory=list)
    recommendation: str = ""
