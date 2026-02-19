# type: ignore
"""
CV-to-Job Analysis Crew.

This module orchestrates the process of comparing a candidate's CV against
matching job descriptions. It employs a sequential workflow where gap
analysis informs the generation of interview questions.
"""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from src.constants import GUARDRAIL_MAX_RETRIES
from src.llm.llm_config import openrouter_llm
from src.talent_selection_flow.crews.cv_to_job_crew.schemas import GapAnalysisOutput, InterviewQuestionsOutput
from src.talent_selection_flow.crews.guardrails import (
    validate_gapanalysisoutput_schema,
    validate_interviewquestionsoutput_schema,
)


@CrewBase
class CVToJobCrew:
    """
    Orchestrates agents to analyze CV alignment with multiple job roles.

    This crew follows a linear pipeline:
    1. Gap Identification: Audit the candidate against job requirements.
    2. Interview Strategy: Generate probing questions based on the audit.

    Attributes:
        agents_config (str): Path to YAML defining the Gap Identifier and Interviewer agents.
        tasks_config (str): Path to YAML defining the audit and question generation tasks.
        _guardrail_max_retries (int): Allowed attempts for LLM self-correction.
        _verbose (bool): If True, enables detailed execution logs.
    """

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(
        self,
        guardrail_max_retries: int = GUARDRAIL_MAX_RETRIES,
        verbose: bool = False,
    ) -> None:
        """Initializes the CV-to-Job evaluation crew."""
        self._guardrail_max_retries = guardrail_max_retries
        self._verbose = verbose

    @agent
    def gap_identifier_agent(self) -> Agent:
        """
        Agent: Technical Auditor.
        Specializes in cross-referencing CV experience with Job 'must-haves'.
        """
        return Agent(
            config=self.agents_config["gap_identifier_agent"],
            llm=openrouter_llm,
        )

    @agent
    def interview_question_generator_agent(self) -> Agent:
        """
        Agent: Interview Strategist.
        Specializes in behavioral and technical questioning based on gap data.
        """
        return Agent(
            config=self.agents_config["interview_question_generator_agent"],
            llm=openrouter_llm,
        )

    @task
    def identify_gaps_task(self) -> Task:
        """
        Task: Perform Gap Analysis.
        Validates output against GapAnalysisOutput schema using custom guardrails.
        """
        task_config = self.tasks_config["identify_gaps_task"]
        return Task(
            description=task_config["description"],
            expected_output=task_config["expected_output"],
            agent=self.gap_identifier_agent(),
            guardrail=validate_gapanalysisoutput_schema,
            guardrail_max_retries=self._guardrail_max_retries,
            output_json=GapAnalysisOutput,
        )

    @task
    def generate_interview_questions_task(self) -> Task:
        """
        Task: Generate Interview Questions.
        Takes the output of 'identify_gaps_task' as context to ensure questions
        target specific missing skills.
        """
        task_config = self.tasks_config["generate_interview_questions_task"]
        return Task(
            description=task_config["description"],
            expected_output=task_config["expected_output"],
            agent=self.interview_question_generator_agent(),
            context=[self.identify_gaps_task()],  # Explicit dependency
            guardrail=validate_interviewquestionsoutput_schema,
            guardrail_max_retries=self._guardrail_max_retries,
            output_json=InterviewQuestionsOutput,
        )

    @crew
    def crew(self) -> Crew:
        """
        Assembles the CV-to-Job crew using a sequential process.
        """
        return Crew(
            name="CV to Job crew",
            agents=[
                self.gap_identifier_agent(),
                self.interview_question_generator_agent(),
            ],
            tasks=[
                self.identify_gaps_task(),
                self.generate_interview_questions_task(),
            ],
            process=Process.sequential,
            verbose=self._verbose,
        )
