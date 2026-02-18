# type: ignore
"""
Metadata Extraction Crews.

This module defines specialized crews for extracting structured information
from CVs and Job Descriptions. These crews serve as the bridge between
raw text input and the structured state required for downstream matching
and analysis tasks.
"""

from crewai import Agent, Crew, Task
from crewai.project import CrewBase, agent, crew, task

from src.constants import GUARDRAIL_MAX_RETRIES
from src.llm.llm_config import openrouter_llm
from src.talent_selection_flow.crews.metadata_extraction_crew.guardrails import (
    validate_cvmetadata_schema,
    validate_jobmetadata_schema,
)
from src.talent_selection_flow.crews.metadata_extraction_crew.schemas import CVMetadata, JobMetadata


@CrewBase
class CVMetadataExtractorCrew:
    """
    Orchestrates the extraction of candidate entities from a CV.

    This crew identifies key personal details, education history, and
    technical skills. It enforces strict schema validation to ensure
    the data can be correctly indexed in the vector database.

    Attributes:
        agents_config (str): Path to YAML defining the CV extractor agent.
        tasks_config (str): Path to YAML defining the CV extraction task.
    """

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(
        self,
        guardrail_max_retries: int = GUARDRAIL_MAX_RETRIES,
        human_input: bool = False,
        verbose: bool = False,
    ) -> None:
        """
        Initializes the CV Extractor Crew.

        Args:
            guardrail_max_retries (int): Attempts for the LLM to fix schema errors.
            human_input (bool): If True, pauses for human review of the metadata.
            verbose (bool): If True, logs internal agent reasoning.
        """
        self._guardrail_max_retries = guardrail_max_retries
        self._human_input = human_input
        self._verbose = verbose

    @agent
    def metadata_extractor_agent(self) -> Agent:
        """
        Agent: CV Entity Recognizer.
        Uses the 'cv_metadata_extractor_agent' configuration from YAML.
        """
        return Agent(
            config=self.agents_config["cv_metadata_extractor_agent"],
            llm=openrouter_llm,
        )

    @task
    def extract_metadata_task(self) -> Task:
        """
        Task: Map CV text to the CVMetadata Pydantic model.
        Uses 'validate_cvmetadata_schema' as a secondary guardrail.
        """
        return Task(
            config=self.tasks_config["extract_cv_metadata_task"],
            agent=self.metadata_extractor_agent(),
            guardrail=validate_cvmetadata_schema,
            guardrail_max_retries=self._guardrail_max_retries,
            output_json=CVMetadata,
            human_input=self._human_input,
        )

    @crew
    def crew(self) -> Crew:
        """Assembles the CV metadata extraction crew."""
        return Crew(
            name="CV metadata extraction crew",
            agents=[self.metadata_extractor_agent()],
            tasks=[self.extract_metadata_task()],
            verbose=self._verbose,
        )


@CrewBase
class JobMetadataExtractorCrew:
    """
    Orchestrates the extraction of role requirements from a Job Description.

    This crew focuses on distilling job titles, required experience levels,
    and mandatory skills into a structured format for matching against CVs.

    Attributes:
        agents_config (str): Path to YAML defining the Job extractor agent.
        tasks_config (str): Path to YAML defining the Job extraction task.
    """

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(
        self, guardrail_max_retries: int = GUARDRAIL_MAX_RETRIES, human_input: bool = False, verbose: bool = False
    ) -> None:
        """Initializes the Job Extractor Crew."""
        self._guardrail_max_retries = guardrail_max_retries
        self._human_input = human_input
        self._verbose = verbose

    @agent
    def metadata_extractor_agent(self) -> Agent:
        """
        Agent: Job Requirement Analyst.
        Uses the 'job_metadata_extractor_agent' configuration from YAML.
        """
        return Agent(
            config=self.agents_config["job_metadata_extractor_agent"],
            llm=openrouter_llm,
        )

    @task
    def extract_metadata_task(self) -> Task:
        """
        Task: Map Job text to the JobMetadata Pydantic model.
        Uses 'validate_jobmetadata_schema' as a secondary guardrail.
        """
        return Task(
            config=self.tasks_config["extract_job_metadata_task"],
            agent=self.metadata_extractor_agent(),
            guardrail=validate_jobmetadata_schema,
            guardrail_max_retries=self._guardrail_max_retries,
            output_json=JobMetadata,
            human_input=self._human_input,
        )

    @crew
    def crew(self) -> Crew:
        """Assembles the Job metadata extraction crew."""
        return Crew(
            name="Job metadata extraction crew",
            agents=[self.metadata_extractor_agent()],
            tasks=[self.extract_metadata_task()],
            verbose=self._verbose,
        )
