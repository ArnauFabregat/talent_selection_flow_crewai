from crewai.flow.flow import Flow, listen, router, start, or_
from pydantic import BaseModel
from typing import Any,  Optional
from enum import StrEnum

from src.talent_selection_flow.crews.classification_crew.crew import ClassificationCrew
from src.talent_selection_flow.crews.cv_to_job_crew.crew import CVToJobCrew
# from src.talent_selection_flow.crews.job_to_cv_crew.crew import JobToCVCrew


class InputType(StrEnum):
    CV = "cv"
    JOB = "job"
    OTHER = "other"


class TalentState(BaseModel):
    raw_input: str = None
    input_type: InputType = InputType.OTHER
    results: Optional[str] = None


class TalentSelectionFlow(Flow[TalentState]):
    """
    Docstring for TalentSelectionFlow
    """

    @start()
    def classify_input(self) -> str:
        result = ClassificationCrew().crew().kickoff(
            inputs={"user_input": self.state.raw_input,
                    "output_options": "/".join(InputType)}
        )
        self.state.input_type = result.raw
        return self.state.input_type

    @router(classify_input)
    def route_by_type(self, result: str) -> str:
        if result == InputType.CV:
            return "handle_cv"
        elif result == InputType.JOB:
            return "handle_job"
        return "handle_unknown"

    @listen("handle_cv")
    def handle_cv(self) -> Any:
        result = CVToJobCrew().crew().kickoff(
            inputs={"content": self.state.raw_input}
        )
        self.state.results = result.raw
        return result

    @listen("handle_job")
    def handle_job(self) -> Any:
        return("Crew not implemented yet.")
        # return JobToCVCrew().crew().kickoff(
        #     inputs={"content": self.state.raw_input}
        # )

    @listen("handle_unknown")
    def handle_unknown(self) -> None:
        # TODO add custom error and import from exceptions.py
        raise ValueError(f"Invalid input type: '{self.state.input_type}'. Expected 'cv' or 'job'")

    @listen(or_(handle_cv, handle_job))
    def summarize_results(self) -> None:
        print(f"Final output:\n{self.state.results}")


# def kickoff() -> None:
#     flow = TalentSelectionFlow()
#     flow.kickoff(inputs={"raw_input": "Your CV or job description here..."})


# if __name__ == "__main__":
#     kickoff()
