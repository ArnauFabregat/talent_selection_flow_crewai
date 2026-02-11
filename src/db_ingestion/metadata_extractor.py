# @CrewBase class: wires YAML agents+tasks into a Crew
from crewai import Agent, Crew, Task

from src.talent_selection_flow.llm.llm_config import groq_llm
from src.db_ingestion.schemas import CVMetadata, JobMetadata


class CVMetadataExtractorCrew:
    """
    Agent extracts metadata from CVs
    """
    def crew(self) -> Crew:
        metadata_extractor_agent = Agent(
            role="CV Metadata Extractor",
            goal="Extract structured metadata from CV text",
            backstory="You are an expert HR analyst who extracts structured info from unstructured CVs",
            llm=groq_llm,
            verbose=True,
        )

        extract_metadata_task = Task(
            description="Extract metadata for this CV: {content}",
            expected_output="""Extract CV metadata with:
                            - skills: comma-separated list of technical and soft skills
                            - industries: comma-separated relevant industries
                            - experience_level: one of intern/entry/intermediate/senior
                            - years_experience: numeric value if mentioned
                            - country: candidate's location
                            - summary: 2-3 sentence overview of the candidate
                            - education_level: one of highschool/bachelor/master/phd/other
                            - languages: comma-separated languages spoken
                            """,
            agent=metadata_extractor_agent,
            output_pydantic=CVMetadata,
        )

        return Crew(
            agents=[metadata_extractor_agent],
            tasks=[extract_metadata_task],
            verbose=True,
        )


class JobMetadataExtractorCrew:
    """
    Agent extracts metadata from job descriptions
    """
    def crew(self) -> Crew:
        metadata_extractor_agent = Agent(
            role="Job Metadata Extractor",
            goal="Extract structured metadata from job description text",
            backstory="You are an expert HR analyst who extracts structured info from unstructured job descriptions",
            llm=groq_llm,
            verbose=True,
        )

        extract_metadata_task = Task(
            description="Extract metadata for this job description: {content}",
            expected_output="""Extract job posting metadata with:
                            - title: exact job title as stated
                            - required_skills: comma-separated list of required skills
                            - skills: comma-separated list of all mentioned skills (required + preferred)
                            - industries: comma-separated relevant industries
                            - experience_level: one of intern/entry/intermediate/senior
                            - years_experience: numeric value if mentioned
                            - country: job location country
                            - city: job location city
                            - summary: 2-3 sentence overview of the role
                            - employment_type: full-time/part-time/contract/freelance if mentioned
                            - responsibilities: comma-separated key job responsibilities
                            """,
            agent=metadata_extractor_agent,
            output_pydantic=JobMetadata,
        )

        return Crew(
            agents=[metadata_extractor_agent],
            tasks=[extract_metadata_task],
            verbose=True,
        )
