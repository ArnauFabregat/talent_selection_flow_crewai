import asyncio
import chainlit as cl

def crewai_step_callback(agent_output):
    """
    Safely bridges the synchronous CrewAI step into the 
    asynchronous Chainlit UI without needing 'run_sync'.
    """
    # 1. Resolve agent name and thought safely
    agent_name = getattr(agent_output, 'agent', 'Agent')
    thought_log = getattr(agent_output, 'thought', '')
    
    if not thought_log and hasattr(agent_output, 'log'):
        thought_log = agent_output.log

    # 2. Get the main event loop
    try:
        loop = cl.get_context().loop
    except Exception:
        # Fallback if context is tricky
        return 

    # 3. Define the async work
    async def create_step():
        async with cl.Step(name=agent_name, type="tool") as step:
            step.output = thought_log

    # 4. Schedule it safely on the main loop
    asyncio.run_coroutine_threadsafe(create_step(), loop)
