from pydantic import BaseModel, Field
from typing import List, Dict


class GapAnalysis(BaseModel):
    matched_skills: List[str] = Field(
        description="Skills evidenced in the CV that match the job requirements."
    )
    missing_must_have: List[str] = Field(
        description="Must-have requirements not evidenced in the CV."
    )


class GapAnalysisOutput(BaseModel):
    docs: Dict[str, GapAnalysis] = Field(
        description="Mapping of cv_id to its gap analysis result."
    )


class QuestionItem(BaseModel):
    question: str = Field(description="The interview question text.")
    response: str = Field(description="The correct response to the question.")


class Questions(BaseModel):
    matched_skill_questions: List[QuestionItem] = Field(
        description="Questions validating matched skills."
    )
    gap_probing_questions: List[QuestionItem] = Field(
        description="Questions exploring must-have gaps."
    )
    ambiguity_clarification_questions: List[QuestionItem] = Field(
        description="Questions clarifying unclear information."
    )
    seniority_questions: List[QuestionItem] = Field(
        description="Questions assessing seniority alignment."
    )


class InterviewQuestionsOutput(BaseModel):
    docs: Dict[str, Questions] = Field(description="Mapping of cv_id to its interview question set.")
