import os
from dotenv import load_dotenv
from crewai import LLM

# Load environment variables from .env file
load_dotenv()

groq_llm = LLM(
    model=os.getenv("LLM_GROQ_MODEL"),
    api_key=os.getenv("LLM_GROQ_API_KEY"),
    temperature=0.7,  # [0, 2] Deterministic to creative responses
    max_tokens=2048,
)


gemini_llm = LLM(
    model=os.getenv("LLM_GEMINI_MODEL"),
    api_key=os.getenv("LLM_GEMINI_API_KEY"),
    temperature=0.7,
    top_p=0.9,
    top_k=40,  # Top-k sampling parameter
    max_output_tokens=2048,
    stop_sequences=["END", "STOP"],
    stream=True,  # Enable streaming
    safety_settings={
        "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
        "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE"
    }
)
