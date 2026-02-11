import chainlit as cl
from src.talent_selection_flow.main import TalentSelectionFlow


@cl.on_message
async def handle_message(message: cl.Message) -> None:
    """
    Orchestrates the TalentSelectionFlow based on user input from Chainlit frontend
    """
    user_input = message.content
    result = TalentSelectionFlow.kickoff({"raw_input": user_input})
    await cl.Message(content=result).send()
