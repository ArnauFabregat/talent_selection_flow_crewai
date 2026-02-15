# @CrewBase class: wires YAML agents+tasks into a Crew
# type: ignore
import os
from pathlib import Path

from dotenv import load_dotenv
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from src.constants import GUARDRAIL_MAX_RETRIES
from src.config.paths import REPORT_OUTPUT_PATH
from src.llm.llm_config import openrouter_llm
from src.talent_selection_flow.crews.cv_to_job_crew.schemas import GapAnalysisOutput, InterviewQuestionsOutput


@CrewBase
class CVToJobCrew:
    """
    CV → Related Jobs → Gaps → Interview Questions → Final Report
    YAML-first configuration:
      - config/agents.yaml
      - config/tasks.yaml
    """

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(self,
                 guardrail_max_retries: int = GUARDRAIL_MAX_RETRIES,
                 verbose: bool = False,
    ) -> None:
        load_dotenv()
        # Ensure report directory exists
        Path(REPORT_OUTPUT_PATH).parent.mkdir(parents=True, exist_ok=True)

        self._guardrail_max_retries = guardrail_max_retries
        self._verbose = verbose

    # -----------------------
    # Agents
    # -----------------------
    @agent
    def gap_identifier_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["gap_identifier_agent"],
            llm=openrouter_llm,
        )

    @agent
    def interview_question_generator_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["interview_question_generator_agent"],
            llm=openrouter_llm,
        )

    @agent
    def report_writer_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["report_writer_agent"],
            llm=openrouter_llm,
        )

    # -----------------------
    # Tasks
    # -----------------------
    @task
    def identify_gaps_task(self) -> Task:
        task_config = self.tasks_config["identify_gaps_task"]
        return Task(
            description=task_config["description"],
            expected_output=task_config["expected_output"],
            agent=self.gap_identifier_agent(),
            guardrail_max_retries=self._guardrail_max_retries,
            output_json=GapAnalysisOutput,
        )

    @task
    def generate_interview_questions_task(self) -> Task:
        task_config = self.tasks_config["generate_interview_questions_task"]
        return Task(
            description=task_config["description"],
            expected_output=task_config["expected_output"],
            agent=self.interview_question_generator_agent(),
            context=[self.retrieve_jobs_task(), self.identify_gaps_task()],
            guardrail_max_retries=self._guardrail_max_retries,
            output_json=InterviewQuestionsOutput,
        )

    @task
    def write_report_task(self) -> Task:
        task_config = self.tasks_config["write_report_task"]
        return Task(
            description=task_config["description"],
            expected_output=task_config["expected_output"],
            agent=self.report_writer_agent(),
            context=[
                self.retrieve_jobs_task(),
                self.identify_gaps_task(),
                self.generate_interview_questions_task(),
            ],
            guardrail_max_retries=self._guardrail_max_retries,
            markdown=True,
            output_file=REPORT_OUTPUT_PATH,
        )

    # -----------------------
    # Crew
    # -----------------------
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[
                self.gap_identifier_agent(),
                self.interview_question_generator_agent(),
                self.report_writer_agent(),
            ],
            tasks=[
                self.identify_gaps_task(),
                self.generate_interview_questions_task(),
                self.write_report_task(),
            ],
            process=Process.sequential,
            verbose=self._verbose,
        )
