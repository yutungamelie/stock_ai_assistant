from langchain_google_genai import ChatGoogleGenerativeAI
from env_settings import EnvSettings


def get_llm() -> ChatGoogleGenerativeAI:
    settings = EnvSettings()

    return ChatGoogleGenerativeAI(
        google_api_key=settings.GOOGLE_API_KEY,
        model=settings.GEMINI_MODEL,
        temperature=0.2,
    )