"""
Recruitment Analysis Schemas.

This module defines the structured data models for gap analysis and
interview question generation. These schemas are used as 'output_json'
targets for CrewAI tasks to ensure strict data formatting.
"""

from pydantic import BaseModel, Field


class GapAnalysis(BaseModel):
    """
    Structured comparison between a candidate's profile and job requirements.

    Attributes:
        matched_skills (list[str]): A list of technical or soft skills found in
            the CV that directly satisfy the job description.
        missing_must_have (list[str]): Critical requirements or 'deal-breakers'
            from the job description that were not found in the candidate's CV.
    """

    matched_skills: list[str] = Field(description="Skills evidenced in the CV that match the job requirements.")
    missing_must_have: list[str] = Field(description="Must-have requirements not evidenced in the CV.")


class QuestionItem(BaseModel):
    """
    A single interview component consisting of a question and its expected answer.

    Attributes:
        question (str): The specific question to be asked by the interviewer.
        response (str): The 'gold standard' or ideal response the interviewer
            should look for based on the job context.
    """

    question: str = Field(description="The interview question text.")
    response: str = Field(description="The correct response to the question.")


class Questions(BaseModel):
    """
    A comprehensive interview guide categorized by assessment goals.

    Attributes:
        matched_skill_questions (list[QuestionItem]): Designed to verify the
            proficiency level of skills the candidate claims to have.
        gap_probing_questions (list[QuestionItem]): Strategically designed to
            see if the candidate possesses 'missing' skills not mentioned in the CV.
        ambiguity_clarification_questions (list[QuestionItem]): Aimed at
            resolving vague dates, broad job titles, or unclear responsibilities.
        seniority_questions (list[QuestionItem]): Aimed at determining if the
            candidate's leadership and decision-making level match the role.
    """

    matched_skill_questions: list[QuestionItem] = Field(description="Questions validating matched skills.")
    gap_probing_questions: list[QuestionItem] = Field(description="Questions exploring must-have gaps.")
    ambiguity_clarification_questions: list[QuestionItem] = Field(
        description="Questions clarifying unclear information."
    )
    seniority_questions: list[QuestionItem] = Field(description="Questions assessing seniority alignment.")
