import os
from dotenv import load_dotenv
from crewai import LLM

# Load environment variables from .env file
load_dotenv()

groq_llm = LLM(
    model=os.getenv("LLM_GROQ_MODEL"),
    api_key=os.getenv("LLM_GROQ_API_KEY"),
    temperature=0.6,  # [0, 2] Deterministic to creative responses
    max_tokens=2048,
)


gemini_llm = LLM(
    model=os.getenv("LLM_GEMINI_MODEL"),
    api_key=os.getenv("LLM_GEMINI_API_KEY"),
    temperature=0.6,
    top_p=0.9,
    top_k=40,  # Top-k sampling parameter
    max_output_tokens=2048,
)


openrouter_llm = LLM(
    model=os.getenv("LLM_OPENROUTER_MODEL"),
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("LLM_OPENROUTER_API_KEY"),
    temperature=0.6,
)
