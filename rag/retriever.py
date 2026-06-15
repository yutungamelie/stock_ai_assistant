from pathlib import Path

from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from env_settings import EnvSettings


BASE_DIR = Path(__file__).resolve().parent.parent
VECTOR_DB_DIR = BASE_DIR / "vector_db" / "investment_rules"


def get_investment_retriever(k: int = 4):
    settings = EnvSettings()

    embeddings = GoogleGenerativeAIEmbeddings(
        google_api_key=settings.GOOGLE_API_KEY,
        model="models/gemini-embedding-001",
    )

    vector_store = Chroma(
        persist_directory=str(VECTOR_DB_DIR),
        embedding_function=embeddings,
        collection_name="investment_rules",
    )

    return vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k},
    )


def search_investment_rules(question: str, k: int = 4):
    retriever = get_investment_retriever(k=k)
    return retriever.invoke(question)


if __name__ == "__main__":
    docs = search_investment_rules("為什麼台積電漲太多要觀望？")

    for i, doc in enumerate(docs, start=1):
        print(f"\n--- Document {i} ---")
        print(f"來源：{doc.metadata.get('filename')}")
        print(doc.page_content)