from pydantic import BaseModel, Field
from typing import List, Dict


class JobGapAnalysis(BaseModel):
    overall_fit_score: float = Field(
        description="Similarity score from ChromaDB for this job."
    )
    matched_skills: List[str] = Field(
        description="Skills evidenced in the CV that match the job requirements."
    )
    missing_must_have: List[str] = Field(
        description="Must-have requirements not evidenced in the CV."
    )
    missing_nice_to_have: List[str] = Field(
        description="Nice-to-have requirements not evidenced in the CV."
    )


class GapAnalysisOutput(BaseModel):
    jobs: Dict[str, JobGapAnalysis] = Field(
        description="Mapping of job_id to its gap analysis result."
    )


class QuestionItem(BaseModel):
    question: str = Field(description="The interview question text.")
    response: str = Field(description="The correct response to the question.")


class JobQuestions(BaseModel):
    matched_skill_questions: List[QuestionItem] = Field(
        description="Questions validating matched skills."
    )
    gap_probing_questions: List[QuestionItem] = Field(
        description="Questions exploring must-have gaps."
    )
    ambiguity_clarification_questions: List[QuestionItem] = Field(
        description="Questions clarifying unclear information."
    )
    seniority_question: QuestionItem = Field(
        description="A single question assessing seniority alignment."
    )


class InterviewQuestionsOutput(BaseModel):
    jobs: Dict[str, JobQuestions] = Field(description="Mapping of job_id to its interview question set.")
