from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from env_settings import EnvSettings


BASE_DIR = Path(__file__).resolve().parent.parent
RAG_DOCS_DIR = BASE_DIR / "rag_docs"
VECTOR_DB_DIR = BASE_DIR / "vector_db" / "investment_rules"


def load_markdown_documents() -> list[Document]:
    documents = []

    for file_path in RAG_DOCS_DIR.glob("*.md"):
        text = file_path.read_text(encoding="utf-8")

        doc = Document(
            page_content=text,
            metadata={
                "source": str(file_path),
                "filename": file_path.name,
            },
        )
        documents.append(doc)

    return documents


def build_vector_db() -> None:
    settings = EnvSettings()

    documents = load_markdown_documents()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        separators=["\n\n", "\n", "。", "，", " ", ""],
    )

    chunks = splitter.split_documents(documents)

    embeddings = GoogleGenerativeAIEmbeddings(
        google_api_key=settings.GOOGLE_API_KEY,
        model="models/gemini-embedding-001",
    )

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(VECTOR_DB_DIR),
        collection_name="investment_rules",
    )

    print(f"原始文件數量：{len(documents)}")
    print(f"切分後 chunk 數量：{len(chunks)}")
    print(f"向量資料庫位置：{VECTOR_DB_DIR}")
    print("RAG 知識庫建立完成。")


if __name__ == "__main__":
    build_vector_db()