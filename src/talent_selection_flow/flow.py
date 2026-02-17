from crewai.flow.flow import Flow, listen, router, start, or_
from typing import Any
import json
from pathlib import Path

from src.config.paths import REPORT_OUTPUT_PATH
from src.constants import GUARDRAIL_MAX_RETRIES
from src.utils.logger import logger

from src.db_ingestion.chroma_client import query_to_collection
from src.talent_selection_flow.schemas import TalentState
from src.talent_selection_flow.crews.utils import render_to_markdown
from src.talent_selection_flow.crews.metadata_extraction_crew.crews import CVMetadataExtractorCrew, JobMetadataExtractorCrew
from src.talent_selection_flow.crews.metadata_extraction_crew.enums import ExperienceLevel, EducationLevel, EmploymentType
from src.talent_selection_flow.crews.classification_crew.enums import DocumentType
from src.talent_selection_flow.crews.classification_crew.crew import ClassificationCrew
from src.talent_selection_flow.crews.cv_to_job_crew.crew import CVToJobCrew
from src.talent_selection_flow.crews.job_to_cv_crew.crew import JobToCVCrew


class TalentSelectionFlow(Flow[TalentState]):
    """
    Docstring for TalentSelectionFlow
    """

    def __init__(self,
                 guardrail_max_retries: int = GUARDRAIL_MAX_RETRIES,
                 verbose: bool = False
    ):
        super().__init__()
        self._guardrail_max_retries = guardrail_max_retries
        self._verbose = verbose

        # Ensure the directory exists
        Path(REPORT_OUTPUT_PATH).parent.mkdir(parents=True, exist_ok=True)

    @start()
    def classify_input(self) -> str:
        result = ClassificationCrew(
            verbose=self._verbose,
            guardrail_max_retries=self._guardrail_max_retries,
        ).crew().kickoff(inputs={
            "user_input": self.state.raw_input,
            "output_options": "/".join(DocumentType),
        })
        self.state.input_type = result.raw

    @router(classify_input)
    def route_by_type(self) -> str:
        if self.state.input_type == DocumentType.CV:
            return "route_cv"
        elif self.state.input_type == DocumentType.JOB:
            return "route_job"
        return "route_other"

    @listen("route_cv")
    def process_cv(self) -> Any:
        # Extract cv metadata
        metadata = CVMetadataExtractorCrew(
            guardrail_max_retries=self._guardrail_max_retries,
            verbose=self._verbose,
            human_input=False,
        ).crew().kickoff(inputs={
            "content": self.state.raw_input,
            "educationlevel_options": "/".join(EducationLevel),
            "experiencelevel_options": "/".join(ExperienceLevel),
        })
        metadata_dict = json.loads(metadata.raw)

        # Get matches from jobs collection
        related_jobs = query_to_collection(
            collection_name="jobs",
            query_text=self.state.raw_input,
            country=metadata_dict.get("country"),
            top_k=3,
        )

        # Send info to CVToJobCrew
        cv_crew = CVToJobCrew(
            verbose=self._verbose,
            guardrail_max_retries=self._guardrail_max_retries,
        )
        _ = cv_crew.crew().kickoff(
            inputs={"structured_cv": metadata_dict,
                    "related_jobs": related_jobs}
        )

        # Markdown Report generation
        report = render_to_markdown(
            process_type="cv",
            metadata_dict=metadata_dict,
            related_docs=related_jobs,
            gap_analysis_output=cv_crew.identify_gaps_task().output.json_dict,
            inverview_questions_output=cv_crew.generate_interview_questions_task().output.json_dict,
        )

        # Write the file
        REPORT_OUTPUT_PATH.write_text(report, encoding="utf-8")
        self.state.output = report
        return report

    @listen("route_job")
    def process_job(self) -> Any:
        # Extract job metadata
        metadata = JobMetadataExtractorCrew(
            guardrail_max_retries=self._guardrail_max_retries,
            verbose=self._verbose,
            human_input=False,
        ).crew().kickoff(inputs={
            "content": self.state.raw_input,
            "employmenttype_options": "/".join(EmploymentType),
            "experiencelevel_options": "/".join(ExperienceLevel),
        })
        metadata_dict = json.loads(metadata.raw)

        # Get matches from jobs collection
        related_cvs = query_to_collection(
            collection_name="cvs",
            query_text=self.state.raw_input,
            country=metadata_dict.get("country"),
            top_k=3,
        )

        # Send info to JobToCVCrew
        job_crew = JobToCVCrew(
            verbose=self._verbose,
            guardrail_max_retries=self._guardrail_max_retries,
        )
        _ = job_crew.crew().kickoff(
            inputs={"structured_job": metadata_dict,
                    "related_cvs": related_cvs}
        )

        # Markdown Report generation
        report = render_to_markdown(
            process_type="job",
            metadata_dict=metadata_dict,
            related_docs=related_cvs,
            gap_analysis_output=job_crew.identify_gaps_task().output.json_dict,
            inverview_questions_output=job_crew.generate_interview_questions_task().output.json_dict,
        )

        # Write the file
        REPORT_OUTPUT_PATH.write_text(report, encoding="utf-8")
        self.state.output = report
        return report

    @listen("route_other")
    def handle_other(self) -> None:
     msg = f"Invalid document type. Expected '{DocumentType.CV}' or '{DocumentType.JOB}'. " \
            "Please, start a new evaluation."
     logger.warning(msg)
     return msg

# def kickoff() -> None:
#     flow = TalentSelectionFlow()
#     flow.kickoff(inputs={"raw_input": "Your CV or job description here..."})


# if __name__ == "__main__":
#     kickoff()
