# type: ignore
"""
HR Consulting Crew Orchestrator.

This module defines the HRConsultingCrew, which leverages specialized
agents to provide high-level recruitment advice and strategic insights
based on analyzed talent data.
"""

from crewai import Agent, Crew, Task
from crewai.project import CrewBase, agent, crew, task

from src.llm.llm_config import openrouter_llm


@CrewBase
class HRConsultingCrew:
    """
    Orchestrates the strategic consulting phase of the talent flow.

    This crew acts as the final decision-support layer, synthesizing
    technical matching data into actionable HR recommendations, such as
    hiring suitability, candidate potential, or organizational alignment.

    Attributes:
        agents_config (str): Path to the YAML file defining the HR Consultant agent.
        tasks_config (str): Path to the YAML file defining the consulting task.
        _verbose (bool): Whether to log internal agent thought processes.
    """

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(
        self,
        verbose: bool = False,
    ) -> None:
        """
        Initializes the HRConsultingCrew.

        Args:
            verbose (bool): Enables detailed output of agent reasoning steps.
        """
        self._verbose = verbose

    @agent
    def consultant_agent(self) -> Agent:
        """
        Defines the HR Consultant Agent.

        This agent is configured to act as a senior recruitment strategist,
        using instructions from the agents_config YAML.

        Returns:
            Agent: A CrewAI Agent instance specializing in HR consulting.
        """
        return Agent(
            config=self.agents_config["consultant_agent"],
            llm=openrouter_llm,
        )

    @task
    def consulting_task(self) -> Task:
        """
        Defines the high-level consulting task.

        Transforms raw technical gaps and interview questions into a
        cohesive strategic summary or final evaluation report.

        Returns:
            Task: A CrewAI Task instance focused on qualitative analysis.
        """
        task_config = self.tasks_config["consulting_task"]
        return Task(
            description=task_config["description"],
            expected_output=task_config["expected_output"],
            agent=self.consultant_agent(),
        )

    @crew
    def crew(self) -> Crew:
        """
        Assembles the HR Consultant crew.

        Returns:
            Crew: A CrewAI Crew instance ready for strategic synthesis.
        """
        return Crew(
            name="HR Consultant crew",
            agents=[self.consultant_agent()],
            tasks=[self.consulting_task()],
            verbose=self._verbose,
        )
