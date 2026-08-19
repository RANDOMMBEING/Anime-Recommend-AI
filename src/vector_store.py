from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_huggingface import HuggingFaceEmbeddings

class VectorStoreBuilder:
    def __init__(self, csv_path: str, persist_dir: str = "chroma_db"):
        self.csv_path = Path(csv_path).resolve()
        self.persist_dir = Path(persist_dir).resolve()
        self.persist_dir.mkdir(parents=True, exist_ok=True)

        self.embedding = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2"
        )

    def build_and_save_vectorstore(self):
        loader = CSVLoader(
            file_path=str(self.csv_path),
            encoding="utf-8"
        )

        documents = loader.load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=0
        )

        split_docs = splitter.split_documents(documents)

        vectorstore = Chroma.from_documents(
            documents=split_docs,
            embedding=self.embedding,
            persist_directory=str(self.persist_dir)
        )

        return vectorstore  # optional but useful

    def load_vector_store(self):
        return Chroma(
            persist_directory=str(self.persist_dir),
            embedding_function=self.embedding
        )
