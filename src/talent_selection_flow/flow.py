from crewai.flow.flow import Flow, listen, router, start, or_
from typing import Any, Dict
import json

from src.constants import GUARDRAIL_MAX_RETRIES
from src.utils.logger import logger

from src.db_ingestion.metadata_extraction_crew.crews import CVMetadataExtractorCrew, JobMetadataExtractorCrew
from src.db_ingestion.metadata_extraction_crew.enums import ExperienceLevel, EducationLevel, EmploymentType
from src.db_ingestion.chroma_client import query_to_collection

from src.talent_selection_flow.crews.classification_crew.enums import DocumentType
from src.talent_selection_flow.schemas import TalentState
from src.talent_selection_flow.crews.classification_crew.crew import ClassificationCrew
from src.talent_selection_flow.crews.cv_to_job_crew.crew import CVToJobCrew
# from src.talent_selection_flow.crews.job_to_cv_crew.crew import JobToCVCrew


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
            human_input=True,
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
        result = CVToJobCrew(
            verbose=self._verbose,
            guardrail_max_retries=self._guardrail_max_retries,
        ).crew().kickoff(
            inputs={"structured_cv": metadata_dict,
                    "related_jobs": related_jobs}
        )
        self.state.output = result.raw

    @listen("route_job")
    def process_job(self) -> Any:
        logger.warning("`JobToCVCrew` not implemented yet.")
        self.state.output = "`JobToCVCrew` not implemented yet."
        # return JobToCVCrew().crew().kickoff(
        #     inputs={"content": self.state.raw_input}
        # )

    @listen("route_other")
    def handle_other(self) -> None:
     logger.warning(f"Invalid document type: '{self.state.input_type}'. Expected '{DocumentType.CV}' or '{DocumentType.JOB}'")
     self.state.output = f"Invalid document type: '{self.state.input_type}'. Expected '{DocumentType.CV}' or '{DocumentType.JOB}'"

    @listen(or_(process_cv, process_job, handle_other))
    def summarize_results(self) -> None:
        print(f"Final output:\n{self.state.output}")


# def kickoff() -> None:
#     flow = TalentSelectionFlow()
#     flow.kickoff(inputs={"raw_input": "Your CV or job description here..."})


# if __name__ == "__main__":
#     kickoff()
