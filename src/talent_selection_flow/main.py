from crewai.flow.flow import Flow, listen, router, start
from pydantic import BaseModel

from talent_selection_flow.crews.classification_crew.crew import ClassificationCrew
from talent_selection_flow.crews.cv_to_job_crew.crew import CVToJobCrew
from talent_selection_flow.crews.job_to_cv_crew.crew import JobToCVCrew

from typing import Any


class TalentState(BaseModel):
    raw_input: str = ""
    input_type: str = ""
    results: str = ""


class TalentSelectionFlow(Flow[TalentState]):
    """
    Docstring for TalentSelectionFlow
    """

    @start()
    def classify_input(self) -> str:
        result = ClassificationCrew().crew().kickoff(
            inputs={"user_input": self.state.raw_input}
        )
        self.state.input_type = result.raw.strip().lower()
        return self.state.input_type

    @router(classify_input)
    def route_by_type(self, result: str) -> str:
        if result == "cv":
            return "cv"
        elif result == "job":
            return "job"
        return "unknown"

    @listen("cv")
    def handle_cv(self) -> Any:
        return CVToJobCrew().crew().kickoff(
            inputs={"content": self.state.raw_input}
        )

    @listen("job")
    def handle_job(self) -> Any:
        return JobToCVCrew().crew().kickoff(
            inputs={"content": self.state.raw_input}
        )

    @listen("unknown")
    def handle_unknown(self) -> None:
        raise ValueError(f"Invalid input type: '{self.state.input_type}'. Expected 'cv' or 'job'")


def kickoff() -> None:
    flow = TalentSelectionFlow()
    flow.kickoff(inputs={"raw_input": "Your CV or job description here..."})


if __name__ == "__main__":
    kickoff()
