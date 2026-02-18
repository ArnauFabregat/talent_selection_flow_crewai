# type: ignore
"""
Classification Crew Orchestrator.

This module defines the ClassificationCrew, which uses CrewAI's declarative
syntax to map agents and tasks defined in YAML files to functional Python
methods. Its primary purpose is to identify the type of document provided by the user.
"""

from crewai import Agent, Crew, Task
from crewai.project import CrewBase, agent, crew, task

from src.constants import GUARDRAIL_MAX_RETRIES
from src.llm.llm_config import openrouter_llm
from src.talent_selection_flow.crews.classification_crew.guardrails import validate_classifier_output


@CrewBase
class ClassificationCrew:
    """
    Orchestrates the document classification process.

    This crew consists of a single specialized agent tasked with parsing
    unstructured input to determine if it is a CV, a Job Description, or
    other content. It utilizes strict guardrails to ensure output reliability.

    Attributes:
        agents_config (str): Path to the YAML file defining agent personalities.
        tasks_config (str): Path to the YAML file defining task requirements.
        _guardrail_max_retries (int): The number of times the agent is allowed
            to self-correct if the guardrail validation fails.
        _verbose (bool): Whether to output execution logs to the console.
    """

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(
        self,
        guardrail_max_retries: int = GUARDRAIL_MAX_RETRIES,
        verbose: bool = False,
    ) -> None:
        """
        Initializes the ClassificationCrew with runtime configurations.

        Args:
            guardrail_max_retries (int): Maximum attempts for the guardrail loop.
            verbose (bool): Enable or disable detailed logging.
        """
        self._guardrail_max_retries = guardrail_max_retries
        self._verbose = verbose

    @agent
    def parser_agent(self) -> Agent:
        """
        Defines the Parser Agent.

        The agent's role and goal are pulled from the agents_config YAML.

        Returns:
            Agent: A CrewAI Agent instance powered by OpenRouter.
        """
        return Agent(
            config=self.agents_config["parser_agent"],
            llm=openrouter_llm,
        )

    @task
    def parse_task(self) -> Task:
        """
        Defines the document classification task.

        This task includes a custom guardrail function to validate that the
        output is a valid DocumentType enum string.

        Returns:
            Task: A CrewAI Task instance with integrated validation logic.
        """
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
        """
        Assembles the classification crew.

        Returns:
            Crew: A CrewAI Crew instance ready to execute the classification task.
        """
        return Crew(
            name="Document classification crew",
            agents=[self.parser_agent()],
            tasks=[self.parse_task()],
            verbose=self._verbose,
        )
