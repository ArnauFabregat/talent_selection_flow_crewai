from typing import List
import chainlit as cl
from src.talent_selection_flow.flow import TalentSelectionFlow
from src.talent_selection_flow.crews.hr_consultant_crew.crew import HRConsultingCrew


def get_actions() -> List[cl.Action]:
    return [
        cl.Action(name="restart_flow", value="restart", label="🔄 Start New Evaluation", payload={}),
        cl.Action(name="download_report_txt", value="download", label="📥 Download Recruitment Analysis Report",
                  payload={})
    ]


# --- CORE WORKFLOW LOGIC ---
async def run_talent_flow():
    """The main process for uploading and evaluating a candidate"""

    # Selection: PDF or Text
    actions = [
        cl.Action(name="pdf_mode", value="pdf", label="📄 Upload PDF", payload={}),
        cl.Action(name="text_mode", value="text", label="✍️ Paste Text", payload={})
    ]

    choice = await cl.AskActionMessage(
        content="How would you like to provide the candidate's profile?",
        actions=actions,
        timeout=300,
    ).send()

    if choice.get("value") == "pdf":
        files = await cl.AskFileMessage(
            content="Please upload the candidate's Resume (PDF)",
            accept=["data/raw/pdf"]
        ).send()
        input_doc = files[0].path
    else:
        res = await cl.AskUserMessage(content="Please paste the resume text here:").send()
        input_doc = res['output']

    # Visual Orchestration
    async with cl.Step(name="Talent Selection Flow", type="run") as step:
        step.input = "⚙️ Orchestrating agents for evaluation..."
        flow = TalentSelectionFlow(verbose=False)
        result = await cl.make_async(flow.kickoff)(inputs={"raw_input": input_doc})
        step.output = "Evaluation complete."

    # Store the user input in the session for the Q&A loop
    cl.user_session.set("chat_history", [f"User: Please analyze this document: {input_doc}"])

    # Store the result in the session for the Q&A loop
    cl.user_session.set("evaluation_report", result)

    # Final result with Restart Action
    context_note = "\n\n*> 💡 Context: I'm currently tracking the last 6 messages " \
                   "to stay focused on our immediate conversation.*"
    await cl.Message(
        content=f"### ✅ Evaluation Result\n\n{result}\n\n---\n💬 **You can now ask follow-up questions "
                f"about this candidate, or click the button above to reset.**{context_note}",
        actions=get_actions(),
    ).send()


# --- EVENT HANDLERS ---

@cl.on_chat_start
async def start():
    """Initial greeting and start of the flow"""
    await cl.Message(
        content="👋 **Welcome to the Talent Scout Assistant.**\nI'll help you analyze candidates using "
                "Multi-Agent intelligence."
    ).send()
    await run_talent_flow()


@cl.action_callback("restart_flow")
async def on_restart(action):
    """Guide the user to the only 100% reliable reset method"""

    # 1. Visual feedback that the request was heard
    await cl.Message(
        content=(
            "### 🔄 Session Reset Required\n\n"
            "To ensure a completely clean state for the next candidate, please click the **'New Chat'** button "
            "in the top-left sidebar.\n\n"
            "*This clears all agent memory and resets the document parser.*"
        )
    ).send()

    # 2. Remove the restart button to avoid confusion
    await action.remove()


@cl.on_message
async def handle_chat(message: cl.Message):
    """Interactive Q&A loop: Triggered whenever the user types a message"""
    # 1. Configuration
    MAX_HISTORY_MESSAGES = 6  # Keeps the last 3 user/assistant pairs

    report = cl.user_session.get("evaluation_report")
    history = cl.user_session.get("chat_history")

    if not report:
        await cl.Message(content="⚠️ I don't have a candidate report yet. Please upload a resume first!").send()
        return

    # 2. Format the sliding window context
    # We slice the history to take only the last N items
    recent_history = history[-MAX_HISTORY_MESSAGES:]
    context_summary = "\n".join(recent_history)

    async with cl.Step(name="HR Consultant Flow", type="llm") as step:
        step.input = "⚙️ Orchestrating agents for evaluation..."
        crew = HRConsultingCrew(verbose=False)
        res = await cl.make_async(crew.crew().kickoff)(inputs={
            "report": report,
            "context_summary": context_summary,
            "message": message.content,
        })

        # 3. Update history: Add current turn and save back to session
        history.append(f"User: {message.content}")
        history.append(f"Consultant: {res.raw}")
        cl.user_session.set("chat_history", history)
        await cl.Message(content=res.raw, actions=get_actions()).send()
        step.output = "Evaluation complete."


@cl.action_callback("download_report_txt")
async def on_download_txt(action):
    # 1. Retrieve the report from the user session
    report_text = cl.user_session.get("evaluation_report")

    if not report_text:
        await cl.ErrorMessage(content="No report found. Please run an evaluation first!").send()
        return

    # 2. Create the file element (using binary encoding)
    file_element = cl.File(
        content=report_text.encode("utf-8"),
        name="recruitment_analysis_report.txt",
        display="inline"
    )

    # 3. Send the file to the UI
    await cl.Message(
        content="💾 **Your report is ready for download:**",
        elements=[file_element]
    ).send()
