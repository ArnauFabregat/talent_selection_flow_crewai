# type: ignore
"""
Job-to-CV Analysis Crew.

This module orchestrates the evaluation of multiple candidates against a single
job description. It focuses on identifying technical mismatches and
generating targeted interview guides for hiring managers.
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
class JobToCVCrew:
    """
    Orchestrates agents to evaluate multiple CVs against a specific job role.

    Workflow:
    1. Gap Analysis: Compares the job's 'must-haves' against candidate profiles.
    2. Question Generation: Produces a custom interview script for each candidate
       to probe identified technical voids.

    Attributes:
        agents_config (str): Path to YAML defining agent personas.
        tasks_config (str): Path to YAML defining task requirements.
        _guardrail_max_retries (int): Maximum self-correction attempts for the LLM.
        _verbose (bool): If True, logs the internal reasoning of the agents.
    """

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(
        self,
        guardrail_max_retries: int = GUARDRAIL_MAX_RETRIES,
        verbose: bool = False,
    ) -> None:
        """Initializes the Job-to-CV evaluation crew."""
        self._guardrail_max_retries = guardrail_max_retries
        self._verbose = verbose

    @agent
    def gap_identifier_agent(self) -> Agent:
        """
        Agent: Technical Recruiter / Auditor.
        Responsible for objective skill matching and gap identification.
        """
        return Agent(
            config=self.agents_config["gap_identifier_agent"],
            llm=openrouter_llm,
        )

    @agent
    def interview_question_generator_agent(self) -> Agent:
        """
        Agent: Interview Coach.
        Responsible for crafting strategic questions that validate strengths
        and explore missing requirements.
        """
        return Agent(
            config=self.agents_config["interview_question_generator_agent"],
            llm=openrouter_llm,
        )

    @task
    def identify_gaps_task(self) -> Task:
        """
        Task: Identify technical gaps for all matched candidates.
        Outputs a structured GapAnalysisOutput JSON validated by guardrails.
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
        Task: Generate candidate-specific interview scripts.
        Uses the findings from 'identify_gaps_task' as context to ensure
        the questions are not generic.
        """
        task_config = self.tasks_config["generate_interview_questions_task"]
        return Task(
            description=task_config["description"],
            expected_output=task_config["expected_output"],
            agent=self.interview_question_generator_agent(),
            context=[self.identify_gaps_task()],
            guardrail=validate_interviewquestionsoutput_schema,
            guardrail_max_retries=self._guardrail_max_retries,
            output_json=InterviewQuestionsOutput,
        )

    @crew
    def crew(self) -> Crew:
        """
        Assembles the Job-to-CV crew for sequential execution.
        """
        return Crew(
            name="Job to CV crew",
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
