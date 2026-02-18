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
    Docstring for TalentSelectionFlow
    """

    def __init__(
        self,
        guardrail_max_retries: int = GUARDRAIL_MAX_RETRIES,
        verbose: bool = False,
    ) -> None:
        super().__init__()
        self._guardrail_max_retries = guardrail_max_retries
        self._verbose = verbose

        # Ensure the directory exists
        Path(REPORT_OUTPUT_PATH).parent.mkdir(parents=True, exist_ok=True)

    @start()
    def classify_input(self) -> None:
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
        if (self.state.input_type == DocumentType.CV) or (self.state.input_type == DocumentType.JOB):
            return "cv_or_job"
        else:
            return "route_other"

    @listen("cv_or_job")
    def extract_metadata(self) -> Any:
        if self.state.input_type == DocumentType.CV:
            # Extract cv metadata
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
            # Extract job metadata
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
        if self.state.input_type == DocumentType.CV:
            collection_name = "jobs"
        else:
            collection_name = "cvs"

        # Get matches from collection
        related_docs = query_to_collection(
            collection_name=collection_name,
            query_text=self.state.raw_input,
            country=self.state.metadata.get("country"),
            top_k=3,
        )
        self.state.related_docs = related_docs

    @router(query_to_db)
    def route_by_type_2(self) -> str:
        if self.state.input_type == DocumentType.CV:
            return "route_cv"
        else:
            return "route_job"

    @listen("route_cv")
    def process_cv(self) -> None:
        # Send info to CVToJobCrew
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
        # Send info to JobToCVCrew
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
        # Markdown Report generation
        report = render_to_markdown(
            process_type=self.state.input_type,
            metadata_dict=self.state.metadata,
            related_docs=self.state.related_docs,
            gap_analysis_output=self.state.process_crew.identify_gaps_task().output.json_dict,
            inverview_questions_output=self.state.process_crew.generate_interview_questions_task().output.json_dict,
        )

        # Write the file
        REPORT_OUTPUT_PATH.write_text(report, encoding="utf-8")
        return report

    @listen("route_other")
    def handle_other(self) -> None:
        msg = (
            f"Invalid document type. Expected '{DocumentType.CV}' or '{DocumentType.JOB}'. "
            "Please, start a new evaluation."
        )
        logger.warning(msg)
        return msg


# def kickoff() -> None:
#     flow = TalentSelectionFlow()
#     flow.kickoff(inputs={"raw_input": "Your CV or job description here..."})


# if __name__ == "__main__":
#     kickoff()
