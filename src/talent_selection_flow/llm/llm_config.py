from crewai import LLM

groq_llm = LLM(
    model="groq/llama-3.3-70b-versatile",
    base_url="https://api.groq.com/openai/v1",
    api_key="YOUR_GROQ_API_KEY",  # https://console.groq.com
    temperature=0.7  # optional
)
