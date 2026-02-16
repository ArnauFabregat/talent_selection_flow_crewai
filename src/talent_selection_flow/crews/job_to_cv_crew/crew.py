# @CrewBase class: wires YAML agents+tasks into a Crew
# type: ignore
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from src.constants import GUARDRAIL_MAX_RETRIES
from src.llm.llm_config import openrouter_llm
from src.talent_selection_flow.crews.cv_to_job_crew.schemas import GapAnalysisOutput, InterviewQuestionsOutput
from src.talent_selection_flow.crews.guardrails import (
    validate_gapanalysisoutput_schema,
    validate_interviewquestionsoutput_schema,
)


@CrewBase
class JobToCVCrew:
    """
    Job description → Related CVs → Gaps → Interview Questions
    YAML-first configuration:
      - config/agents.yaml
      - config/tasks.yaml
    """

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(self,
                 guardrail_max_retries: int = GUARDRAIL_MAX_RETRIES,
                 verbose: bool = False,
    ) -> None:
        self._guardrail_max_retries = guardrail_max_retries
        self._verbose = verbose

    @agent
    def gap_identifier_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["gap_identifier_agent"],
            llm=openrouter_llm,
        )

    @agent
    def interview_question_generator_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["interview_question_generator_agent"],
            llm=openrouter_llm,
        )

    @task
    def identify_gaps_task(self) -> Task:
        task_config = self.tasks_config["identify_gaps_task"]
        return Task(
            description=task_config["description"],
            expected_output=task_config["expected_output"],
            agent=self.gap_identifier_agent(),
            guardrail=validate_gapanalysisoutput_schema,
            guardrail_max_retries=self._guardrail_max_retries,
            output_json=GapAnalysisOutput,
        )

    @task
    def generate_interview_questions_task(self) -> Task:
        task_config = self.tasks_config["generate_interview_questions_task"]
        return Task(
            description=task_config["description"],
            expected_output=task_config["expected_output"],
            agent=self.interview_question_generator_agent(),
            context=[self.identify_gaps_task()],
            guardrail=validate_interviewquestionsoutput_schema,
            guardrail_max_retries=self._guardrail_max_retries,
            output_json=InterviewQuestionsOutput,
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            name="Job to CV crew",
            agents=[
                self.gap_identifier_agent(),
                self.interview_question_generator_agent(),
            ],
            tasks=[
                self.identify_gaps_task(),
                self.generate_interview_questions_task(),
            ],
            process=Process.sequential,
            verbose=self._verbose,
        )
