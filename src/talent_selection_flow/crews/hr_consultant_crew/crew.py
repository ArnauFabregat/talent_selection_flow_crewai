# @CrewBase class: wires YAML agents+tasks into a Crew
# type: ignore
from crewai import Agent, Crew, Task
from crewai.project import CrewBase, agent, crew, task

from src.llm.llm_config import openrouter_llm


@CrewBase
class HRConsultingCrew:
    """
    Agent parses raw input to determine type
    """

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(self,
                 verbose: bool = False
    ):
        self._verbose = verbose

    @agent
    def consultant_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["consultant_agent"],
            llm=openrouter_llm,
        )

    @task
    def consulting_task(self) -> Task:
        task_config = self.tasks_config["consulting_task"]
        return Task(
            description=task_config["description"],
            expected_output=task_config["expected_output"],
            agent=self.consultant_agent(),
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            name="HR Consultant crew",
            agents=[self.consultant_agent()],
            tasks=[self.consulting_task()],
            verbose=self._verbose,
        )
