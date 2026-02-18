from pydantic import BaseModel, Field


class GapAnalysis(BaseModel):
    matched_skills: list[str] = Field(description="Skills evidenced in the CV that match the job requirements.")
    missing_must_have: list[str] = Field(description="Must-have requirements not evidenced in the CV.")


class QuestionItem(BaseModel):
    question: str = Field(description="The interview question text.")
    response: str = Field(description="The correct response to the question.")


class Questions(BaseModel):
    matched_skill_questions: list[QuestionItem] = Field(description="Questions validating matched skills.")
    gap_probing_questions: list[QuestionItem] = Field(description="Questions exploring must-have gaps.")
    ambiguity_clarification_questions: list[QuestionItem] = Field(
        description="Questions clarifying unclear information."
    )
    seniority_questions: list[QuestionItem] = Field(description="Questions assessing seniority alignment.")
