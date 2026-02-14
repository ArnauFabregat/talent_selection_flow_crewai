# @CrewBase class: wires YAML agents+tasks into a Crew
# type: ignore
import os
from pathlib import Path

from dotenv import load_dotenv
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from src.config.paths import REPORT_OUTPUT_PATH
from src.llm.llm_config import openrouter_llm
from src.talent_selection_flow.tools.chromadb_matcher import ChromaDBMatcherTool
from src.talent_selection_flow.crews.cv_to_job_crew.schemas.match import RetrievalResult
from src.talent_selection_flow.crews.cv_to_job_crew.schemas.report import GapAnalysisOutput, InterviewQuestionsOutput


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

    def __init__(self) -> None:
        load_dotenv()
        # Ensure report directory exists
        out_path = Path(os.getenv(REPORT_OUTPUT_PATH))
        out_path.parent.mkdir(parents=True, exist_ok=True)

    # -----------------------
    # Agents
    # -----------------------
    @agent
    def cv_job_retrieval_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["cv_job_retrieval_agent"],
            tools=[ChromaDBMatcherTool(chroma_path=os.getenv("CHROMA_DB_PATH"))],
            llm=openrouter_llm,
            verbose=True,
        )

    @agent
    def gap_identifier_agent(self) -> Agent:
        # TODO: tool to load job descriptions for the identified job_ids
        return Agent(
            config=self.agents_config["gap_identifier_agent"],
            llm=openrouter_llm,
            verbose=True,
        )

    @agent
    def interview_question_generator_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["interview_question_generator_agent"],
            llm=openrouter_llm,
            verbose=True,
        )

    @agent
    def report_writer_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["report_writer_agent"],
            llm=openrouter_llm,
            verbose=True,
        )

    # -----------------------
    # Tasks
    # -----------------------
    @task
    def retrieve_jobs_task(self) -> Task:
        task_config = self.tasks_config["retrieve_jobs_task"]
        return Task(
            description=task_config["description"],
            expected_output=task_config["expected_output"],
            agent=self.cv_job_retrieval_agent(),
            output_json=RetrievalResult,
        )

    @task
    def identify_gaps_task(self) -> Task:
        task_config = self.tasks_config["identify_gaps_task"]
        return Task(
            description=task_config["description"],
            expected_output=task_config["expected_output"],
            agent=self.gap_identifier_agent(),
            context=[self.retrieve_jobs_task()],
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
                self.cv_job_retrieval_agent(),
                self.gap_identifier_agent(),
                self.interview_question_generator_agent(),
                self.report_writer_agent(),
            ],
            tasks=[
                self.retrieve_jobs_task(),
                self.identify_gaps_task(),
                self.generate_interview_questions_task(),
                self.write_report_task(),
            ],
            process=Process.sequential,
            verbose=True,
        )
