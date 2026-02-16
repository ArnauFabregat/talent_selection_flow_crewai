import chainlit as cl
import builtins

from src.talent_selection_flow.flow import TalentSelectionFlow


# --- HUMAN-IN-THE-LOOP BRIDGE ---
async def ask_human_input(prompt):
    """Intercepts Python's input() and redirects it to the Chainlit UI"""
    res = await cl.AskUserMessage(
        content=f"🤖 **Agent requires clarification:**\n\n{prompt}",
        timeout=600
    ).send()
    if res:
        return res['output']
    return "No response provided by human."

# Globally override the input function
builtins.input = lambda prompt: cl.make_async(ask_human_input)(prompt)

@cl.on_chat_start
async def start():
    # 1. Professional Welcome
    await cl.Message(
        content="👋 **Welcome to the Talent Selection Flow.**\nAutomating candidate screening with Multi-Agent Systems."
    ).send()

    # 2. Input Selection: PDF or Text
    actions = [
            cl.Action(
                name="pdf_mode", 
                value="pdf", 
                label="📄 Upload PDF",
                description="Upload a resume in PDF format",
                payload={},
            ),
            cl.Action(
                name="text_mode", 
                value="text", 
                label="✍️ Paste Text",
                description="Paste the resume content as plain text",
                payload={},
            )
    ]

    choice = await cl.AskActionMessage(
        content="How would you like to provide the candidate's profile?",
        actions=actions,
        timeout=300,
    ).send()

    if choice.get("value") == "pdf":
        files = await cl.AskFileMessage(
            content="Please upload the candidate's Resume (PDF)", 
            accept=["application/pdf"]
        ).send()
        input_doc = files[0].path # We pass the file path
    else:
        res = await cl.AskUserMessage(
            content="Please paste the resume text here:"
        ).send()
        input_doc = res['output']

    await cl.Message(content="⚙️ **Orchestrating Agents...**").send()

    # 3. Initialize the Flow
    flow = TalentSelectionFlow(verbose=False)

    # 4. Execute the CrewAI Flow asynchronously
    result = await cl.make_async(flow.kickoff)(inputs={"raw_input": input_doc})

    # 5. Display Final Validated Result
    await cl.Message(
        content=f"### ✅ Evaluation Complete\n\n{result}"
    ).send()
