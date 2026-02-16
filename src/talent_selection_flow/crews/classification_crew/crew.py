# @CrewBase class: wires YAML agents+tasks into a Crew
# type: ignore
from crewai import Agent, Crew, Task
from crewai.project import CrewBase, agent, crew, task

from src.constants import GUARDRAIL_MAX_RETRIES
from src.llm.llm_config import openrouter_llm
from src.talent_selection_flow.crews.classification_crew.guardrails import validate_classifier_output
# from src.utils.callback import crewai_step_callback


@CrewBase
class ClassificationCrew:
    """
    Agent parses raw input to determine type
    """

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(self,
                 guardrail_max_retries: int = GUARDRAIL_MAX_RETRIES,
                 verbose: bool = False
    ):
        self._guardrail_max_retries = guardrail_max_retries
        self._verbose = verbose

    @agent
    def parser_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["parser_agent"],
            llm=openrouter_llm,
        )

    @task
    def parse_task(self) -> Task:
        task_config = self.tasks_config["parse_task"]
        return Task(
            description=task_config["description"],
            expected_output=task_config["expected_output"],
            agent=self.parser_agent(),
            guardrail=validate_classifier_output,
            guardrail_max_retries=self._guardrail_max_retries,
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            name="Document classification crew",
            agents=[self.parser_agent()],
            tasks=[self.parse_task()],
            # step_callback=crewai_step_callback,
            verbose=self._verbose,
        )
