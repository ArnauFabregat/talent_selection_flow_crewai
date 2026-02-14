# @CrewBase class: wires YAML agents+tasks into a Crew
from crewai import Agent, Crew, Task
from crewai.project import CrewBase, agent, crew, task

from src.constants import GUARDRAIL_MAX_RETRIES
from src.llm.llm_config import openrouter_llm
from src.db_ingestion.metadata_extraction_crew.schemas import CVMetadata, JobMetadata
from src.utils.guardrails import (
    validate_json_output,
    validate_cvmetadata_schema,
    validate_jobmetadata_schema,
)


@CrewBase
class CVMetadataExtractorCrew:
    """
    Agent extracts metadata from CVs
    """
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(self,
                 guardrail_max_retries: int = GUARDRAIL_MAX_RETRIES,
                 verbose: bool = False
    ):
        self._guardrail_max_retries = guardrail_max_retries
        self._verbose = verbose

    @agent
    def metadata_extractor_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["cv_metadata_extractor_agent"],
            llm=openrouter_llm,
        )

    @task
    def extract_metadata_task(self) -> Task:
        return Task(
            config=self.tasks_config["extract_cv_metadata_task"],
            agent=self.metadata_extractor_agent(),
            guardrails=[validate_json_output, validate_cvmetadata_schema],
            guardrail_max_retries=self._guardrail_max_retries,
            output_json=CVMetadata,
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.metadata_extractor_agent()],
            tasks=[self.extract_metadata_task()],
            verbose=self._verbose,
        )


@CrewBase
class JobMetadataExtractorCrew:
    """
    Agent extracts metadata from job descriptions
    """
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(self,
                 guardrail_max_retries: int = GUARDRAIL_MAX_RETRIES,
                 verbose: bool = False
    ):
        self._guardrail_max_retries = guardrail_max_retries
        self._verbose = verbose

    @agent
    def metadata_extractor_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["job_metadata_extractor_agent"],
            llm=openrouter_llm,
        )

    @task
    def extract_metadata_task(self) -> Task:
        return Task(
            config=self.tasks_config["extract_job_metadata_task"],
            agent=self.metadata_extractor_agent(),
            guardrails=[validate_json_output, validate_jobmetadata_schema],
            guardrail_max_retries=self._guardrail_max_retries,
            output_json=JobMetadata,
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.metadata_extractor_agent()],
            tasks=[self.extract_metadata_task()],
            verbose=self._verbose,
        )
