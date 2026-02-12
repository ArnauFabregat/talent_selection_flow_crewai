import os
from dotenv import load_dotenv
from crewai import LLM

# Load environment variables from .env file
load_dotenv()

groq_llm = LLM(
    model=os.getenv("LLM_MODEL"),
    api_key=os.getenv("LLM_API_KEY"),
    temperature=0.7,  # [0, 2] Deterministic to creative responses
    max_tokens=2048,
)
