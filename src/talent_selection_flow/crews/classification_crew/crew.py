# @CrewBase class: wires YAML agents+tasks into a Crew
# type: ignore
from crewai import Agent, Crew, Task
from crewai.project import CrewBase, agent, crew, task

from llm.llm_config import groq_llm
from talent_selection_flow.crews.classification_crew.schemas.input import ParsedInput


@CrewBase
class ClassificationCrew:
    """
    Agent parses raw input to determine type
    """

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def parser_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["parser_agent"],
            llm=groq_llm,
            verbose=True,
        )

    @task
    def parse_task(self) -> Task:
        task_config = self.tasks_config["parse_task"]
        return Task(
            description=task_config["description"],
            expected_output=task_config["expected_output"],
            agent=self.parser_agent(),
            output_pydantic=ParsedInput,
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.parser_agent()],
            tasks=[self.parse_task()],
            verbose=True,
        )
