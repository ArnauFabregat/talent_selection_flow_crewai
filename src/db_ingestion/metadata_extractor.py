# @CrewBase class: wires YAML agents+tasks into a Crew
from crewai import Agent, Crew, Task

from src.llm.llm_config import openrouter_llm
from src.db_ingestion.schemas import CVMetadata, JobMetadata
from src.utils.guardrails import (
    validate_json_output,
    validate_cvmetadata_schema,
    validate_jobmetadata_schema,
)
from src.db_ingestion.enums import ExperienceLevel, EducationLevel, EmploymentType


class CVMetadataExtractorCrew:
    """
    Agent extracts metadata from CVs
    """
    def __init__(self, guardrail_max_retries: int = 3, verbose: bool = False):
        self._guardrail_max_retries = guardrail_max_retries
        self._verbose = verbose

    def crew(self) -> Crew:
        metadata_extractor_agent = Agent(
            role="CV Metadata Extractor",
            goal="Extract structured metadata from CV text",
            backstory="You are an expert HR analyst who extracts structured info from unstructured CVs",
            llm=openrouter_llm,
        )

        extract_metadata_task = Task(
            description=f"""Extract metadata for this CV:\n{{content}}
\nExtract this metadata:
    - skills: comma-separated list of required skills
    - industries: comma-separated relevant industries
    - experience_level: one of {"/".join(ExperienceLevel)}
    - country: candidate's location country in ISO code Alpha-2
    - summary: 2-3 sentence overview of the role
    - education_level: one of {"/".join(EducationLevel)}
    - languages: comma-separated languages spoken or "unknown"
""",
            expected_output="""Return a strict JSON object with the following structure:
{
"skills": "skill1, skill2, ...",
"industries": "industry1, industry2, ...",
"experience_level": "...",
"country": "...",
"summary": "...",
"education_level": "...",
"languages": "language1, language2, ...",
}
Additional rules:
- Only return the JSON — no commentary before or after.
""",
            agent=metadata_extractor_agent,
            guardrails=[validate_json_output, validate_cvmetadata_schema],
            output_json=CVMetadata,
        )

        return Crew(
            agents=[metadata_extractor_agent],
            tasks=[extract_metadata_task],
            verbose=self._verbose,
            guardrail_max_retries=self._guardrail_max_retries
        )


class JobMetadataExtractorCrew:
    """
    Agent extracts metadata from job descriptions
    """
    def __init__(self, guardrail_max_retries: int = 3, verbose: bool = False):
        self._guardrail_max_retries = guardrail_max_retries
        self._verbose = verbose

    def crew(self) -> Crew:
        metadata_extractor_agent = Agent(
            role="Job Metadata Extractor",
            goal="Extract structured metadata from job description text",
            backstory="You are an expert HR analyst who extracts structured info from unstructured job descriptions",
            llm=openrouter_llm,
        )

        extract_metadata_task = Task(
            description=f"""Extract metadata for this job description:\n{{content}}
\nExtract this metadata:
    - title: exact job title as stated
    - skills: comma-separated list of required skills
    - industries: comma-separated relevant industries
    - experience_level: one of {"/".join(ExperienceLevel)}
    - country: job location country in ISO code Alpha-2
    - city: job location city
    - summary: 2-3 sentence overview of the role
    - employment_type: one of {"/".join(EmploymentType)}
    - responsibilities: comma-separated key job responsibilities
""",
            expected_output="""Return a strict JSON object with the following structure:
{
"title": "...",
"skills": "skill1, skill2, ...",
"industries": "industry1, industry2, ...",
"experience_level": "...",
"country": "...",
"city": "...",
"summary": "...",
"employment_type": "...",
"responsibilities": "resp1, resp2",
}
Additional rules:
- Only return the JSON — no commentary before or after.
""",
            agent=metadata_extractor_agent,
            guardrails=[validate_json_output, validate_jobmetadata_schema],
            output_json=JobMetadata,
        )

        return Crew(
            agents=[metadata_extractor_agent],
            tasks=[extract_metadata_task],
            verbose=self._verbose,
            guardrail_max_retries=self._guardrail_max_retries
        )
