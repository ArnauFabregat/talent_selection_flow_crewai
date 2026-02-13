# @CrewBase class: wires YAML agents+tasks into a Crew
from crewai import Agent, Crew, Task

from src.config.params import VERBOSE
from src.llm.llm_config import gemini_llm
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
            llm=gemini_llm,
            verbose=VERBOSE,
        )

        extract_metadata_task = Task(
            description="""Extract metadata for this CV:\n{content}
                        \nExtract this metadata:
                            - skills: comma-separated list of required skills
                            - industries: comma-separated relevant industries
                            - experience_level: one of intern/entry/intermediate/senior
                            - country: candidate's location country in ISO code
                            - summary: 2-3 sentence overview of the role
                            - education_level: one of highschool/bachelor/master/phd/other
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
            output_json=CVMetadata,
        )

        return Crew(
            agents=[metadata_extractor_agent],
            tasks=[extract_metadata_task],
            verbose=VERBOSE,
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
            llm=gemini_llm,
            verbose=VERBOSE,
        )

        extract_metadata_task = Task(
            description="""Extract metadata for this job description:\n{content}
                        \nExtract this metadata:
                            - title: exact job title as stated
                            - skills: comma-separated list of required skills
                            - industries: comma-separated relevant industries
                            - experience_level: one of intern/entry/intermediate/senior
                            - country: job location country in ISO code
                            - city: job location city
                            - summary: 2-3 sentence overview of the role
                            - employment_type: full-time/part-time/contract/freelance if mentioned
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
            output_json=JobMetadata,
        )

        return Crew(
            agents=[metadata_extractor_agent],
            tasks=[extract_metadata_task],
            verbose=VERBOSE,
        )
