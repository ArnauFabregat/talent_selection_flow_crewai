"""
LLM Configurations Module.

This module initializes various Large Language Model (LLM) instances using the
CrewAI LLM wrapper. It centralizes model parameters (temperature, tokens, etc.)
and environment variable management for Groq, Gemini, and OpenRouter providers.
"""

import os

from crewai import LLM
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- GROQ CONFIGURATION ---
# Optimized for high-speed inference and low latency.
groq_llm = LLM(
    model=os.getenv("LLM_GROQ_MODEL", ""),
    api_key=os.getenv("LLM_GROQ_API_KEY"),
    temperature=0.6,  # [0, 2] Controls randomness: 0 is deterministic, 2 is highly creative.
    max_tokens=2048,
)
"""LLM: Groq instance for fast processing and specific Llama/Mistral models."""


# --- GEMINI CONFIGURATION ---
# Google's multimodal model with advanced sampling parameters.
gemini_llm = LLM(
    model=os.getenv("LLM_GEMINI_MODEL", ""),
    api_key=os.getenv("LLM_GEMINI_API_KEY"),
    temperature=0.6,
    top_p=0.9,  # Nucleus sampling: considers the smallest set of tokens whose cumulative probability >= top_p.
    top_k=40,  # Limits the model to the top K most likely next words.
    max_output_tokens=2048,
)
"""LLM: Gemini instance for complex reasoning and large context window tasks."""


# --- OPENROUTER CONFIGURATION ---
# Unified API access to various open-source and proprietary models.
openrouter_llm = LLM(
    model=os.getenv("LLM_OPENROUTER_MODEL", ""),
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("LLM_OPENROUTER_API_KEY"),
    temperature=0.6,
)
"""LLM: OpenRouter instance used as a gateway for diverse model selection."""
