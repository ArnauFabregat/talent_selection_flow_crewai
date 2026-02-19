# type: ignore
"""
Talent Selection Flow Orchestrator.

This module defines the TalentSelectionFlow class, which uses CrewAI Flows
to manage the lifecycle of a talent evaluation. It handles document
classification, metadata extraction, vector database querying, and
multi-agent analysis for both CV-to-Job and Job-to-CV scenarios.
"""

import json
from pathlib import Path
from typing import Any

from crewai.flow.flow import Flow, listen, or_, router, start

from src.config.paths import REPORT_OUTPUT_PATH
from src.constants import GUARDRAIL_MAX_RETRIES
from src.db_ingestion.chroma_client import query_to_collection
from src.talent_selection_flow.crews.classification_crew.crew import ClassificationCrew
from src.talent_selection_flow.crews.classification_crew.enums import DocumentType
from src.talent_selection_flow.crews.cv_to_job_crew.crew import CVToJobCrew
from src.talent_selection_flow.crews.job_to_cv_crew.crew import JobToCVCrew
from src.talent_selection_flow.crews.metadata_extraction_crew.crews import (
    CVMetadataExtractorCrew,
    JobMetadataExtractorCrew,
)
from src.talent_selection_flow.crews.metadata_extraction_crew.enums import (
    EducationLevel,
    EmploymentType,
    ExperienceLevel,
)
from src.talent_selection_flow.crews.utils import render_to_markdown
from src.talent_selection_flow.schemas import TalentState
from src.utils.logger import logger


class TalentSelectionFlow(Flow[TalentState]):
    """
    An asynchronous flow for automated talent and job analysis.

    This flow orchestrates several specialized AI crews to process
    unstructured text, extract relevant entities, find matches in a
    vector database, and generate a final gap analysis report.

    Attributes:
        _guardrail_max_retries (int): Max attempts for self-correction in crews.
        _verbose (bool): Whether to print detailed execution logs.
    """

    def __init__(
        self,
        guardrail_max_retries: int = GUARDRAIL_MAX_RETRIES,
        verbose: bool = False,
    ) -> None:
        """
        Initializes the flow and ensures the output directory exists.

        Args:
            guardrail_max_retries (int): Retries for agentic guardrails.
            verbose (bool): Enable/disable detailed logging.
        """
        super().__init__()
        self._guardrail_max_retries = guardrail_max_retries
        self._verbose = verbose

        # Ensure the directory exists
        Path(REPORT_OUTPUT_PATH).parent.mkdir(parents=True, exist_ok=True)

    @start()
    def classify_input(self) -> None:
        """
        Step 1: Identifies the type of document provided by the user.

        Uses the ClassificationCrew to determine if the input is a CV,
        a Job Description, or something else.
        """
        result = (
            ClassificationCrew(
                verbose=self._verbose,
                guardrail_max_retries=self._guardrail_max_retries,
            )
            .crew()
            .kickoff(
                inputs={
                    "user_input": self.state.raw_input,
                    "output_options": "/".join(DocumentType),
                }
            )
        )
        self.state.input_type = result.raw

    @router(classify_input)
    def route_by_type_1(self) -> str:
        """
        Decision Point 1: Routes to metadata extraction or error handling.

        Returns:
            str: "cv_or_job" for valid types, "route_other" for invalid types.
        """
        if (self.state.input_type == DocumentType.CV) or (self.state.input_type == DocumentType.JOB):
            return "cv_or_job"
        else:
            return "route_other"

    @listen("cv_or_job")
    def extract_metadata(self) -> Any:
        """
        Step 2: Extracts structured entities based on the document type.

        Uses either CVMetadataExtractorCrew or JobMetadataExtractorCrew
        to populate the state metadata (skills, experience, etc.).
        """
        if self.state.input_type == DocumentType.CV:
            metadata = (
                CVMetadataExtractorCrew(
                    guardrail_max_retries=self._guardrail_max_retries,
                    verbose=self._verbose,
                    human_input=False,
                )
                .crew()
                .kickoff(
                    inputs={
                        "content": self.state.raw_input,
                        "educationlevel_options": "/".join(EducationLevel),
                        "experiencelevel_options": "/".join(ExperienceLevel),
                    }
                )
            )
        else:
            metadata = (
                JobMetadataExtractorCrew(
                    guardrail_max_retries=self._guardrail_max_retries,
                    verbose=self._verbose,
                    human_input=False,
                )
                .crew()
                .kickoff(
                    inputs={
                        "content": self.state.raw_input,
                        "employmenttype_options": "/".join(EmploymentType),
                        "experiencelevel_options": "/".join(ExperienceLevel),
                    }
                )
            )
        self.state.metadata = json.loads(metadata.raw)

    @listen(extract_metadata)
    def query_to_db(self) -> Any:
        """
        Step 3: Performs semantic search in ChromaDB.

        Queries the 'jobs' collection if a CV was provided, or the 'cvs'
        collection if a Job Description was provided.
        """
        if self.state.input_type == DocumentType.CV:
            collection_name = "jobs"
        else:
            collection_name = "cvs"

        related_docs = query_to_collection(
            collection_name=collection_name,
            query_text=self.state.raw_input,
            country=self.state.metadata.get("country"),
            top_k=3,
        )
        self.state.related_docs = related_docs

    @router(query_to_db)
    def route_by_type_2(self) -> str:
        """
        Decision Point 2: Selects the appropriate analysis crew.

        Returns:
            str: "route_cv" for candidate-centric analysis or "route_job"
                for recruiter-centric analysis.
        """
        if self.state.input_type == DocumentType.CV:
            return "route_cv"
        else:
            return "route_job"

    @listen("route_cv")
    def process_cv(self) -> None:
        """
        Step 4a: Candidate Analysis.

        Matches a candidate against potential jobs using the CVToJobCrew.
        """
        cv_crew = CVToJobCrew(
            verbose=self._verbose,
            guardrail_max_retries=self._guardrail_max_retries,
        )
        _ = cv_crew.crew().kickoff(
            inputs={"structured_cv": self.state.metadata, "related_jobs": self.state.related_docs}
        )
        self.state.process_crew = cv_crew

    @listen("route_job")
    def process_job(self) -> None:
        """
        Step 4b: Job Analysis.

        Matches a job description against potential candidates using the JobToCVCrew.
        """
        job_crew = JobToCVCrew(
            verbose=self._verbose,
            guardrail_max_retries=self._guardrail_max_retries,
        )
        _ = job_crew.crew().kickoff(
            inputs={"structured_job": self.state.metadata, "related_cvs": self.state.related_docs}
        )
        self.state.process_crew = job_crew

    @listen(or_(process_cv, process_job))
    def render_and_export_report(self) -> str:
        """
        Step 5: Report Finalization.

        Consolidates all metadata, gap analyses, and interview questions
        into a Markdown report and saves it to disk.

        Returns:
            str: The full content of the generated report.
        """
        report = render_to_markdown(
            process_type=self.state.input_type,
            metadata_dict=self.state.metadata,
            related_docs=self.state.related_docs,
            gap_analysis_output=self.state.process_crew.identify_gaps_task().output.json_dict,
            inverview_questions_output=self.state.process_crew.generate_interview_questions_task().output.json_dict,
        )

        REPORT_OUTPUT_PATH.write_text(report, encoding="utf-8")
        return report

    @listen("route_other")
    def handle_other(self) -> str:
        """
        Error Handler: Triggered when input classification fails.
        """
        msg = (
            f"Invalid document type. Expected '{DocumentType.CV}' or '{DocumentType.JOB}'. "
            "Please, start a new evaluation."
        )
        logger.warning(msg)
        return msg
