"""
Vector Store Setup
Creates and manages ChromaDB with local HuggingFace embeddings (no API rate limits)
"""

import os
from typing import List
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from data_ingestion import DataIngestion
from dotenv import load_dotenv

load_dotenv()


class VectorStoreManager:
    def __init__(self, persist_directory="./data/chroma_db"):
        self.persist_directory = persist_directory
        # Use local BAAI/bge-small-en-v1.5 model - fast, small (130MB), no API rate limits!
        self.embeddings = HuggingFaceEmbeddings(
            model_name="BAAI/bge-small-en-v1.5",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        self.vectorstore = None
    
    def create_vectorstore(self, documents: List[Document]):
        """Create a new vector store from documents"""
        print(f"Creating vector store with {len(documents)} documents...")
        
        self.vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )
        
        print(f"Vector store created and persisted at {self.persist_directory}")
        return self.vectorstore
    
    def load_vectorstore(self):
        """Load existing vector store"""
        if not os.path.exists(self.persist_directory):
            raise FileNotFoundError(f"Vector store not found at {self.persist_directory}")
        
        self.vectorstore = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings
        )
        
        print("Vector store loaded successfully")
        return self.vectorstore
    
    def add_documents(self, documents: List[Document]):
        """Add documents to existing vector store"""
        if self.vectorstore is None:
            self.load_vectorstore()
        
        self.vectorstore.add_documents(documents)
        print(f"Added {len(documents)} documents to vector store")
    
    def similarity_search(self, query: str, k: int = 3):
        """Search for similar documents"""
        if self.vectorstore is None:
            self.load_vectorstore()
        
        results = self.vectorstore.similarity_search(query, k=k)
        return results
    
    def similarity_search_with_score(self, query: str, k: int = 3):
        """Search with relevance scores"""
        if self.vectorstore is None:
            self.load_vectorstore()
        
        results = self.vectorstore.similarity_search_with_score(query, k=k)
        return results


def setup_initial_vectorstore():
    """
    Initial setup script to create vector store
    Run this once to set up your knowledge base
    """
    print("=== Setting Up Vector Store ===\n")
    
    # Initialize data ingestion
    ingestion = DataIngestion(chunk_size=1000, chunk_overlap=100)
    
    all_documents = []
    
    # 1. Load from documents directory (supports PDF, TXT, DOCX, XLSX, CSV)
    print("1. Loading documents from ./data/documents/")
    print("   Supported formats: PDF, TXT, DOCX, XLSX, CSV")
    docs_from_dir = ingestion.load_directory("./data/documents")
    all_documents.extend(docs_from_dir)
    print(f"   Loaded {len(docs_from_dir)} chunks\n")
    
    # 2. Create vector store
    if len(all_documents) == 0:
        print("❌ No documents loaded. Please add documents to ./data/documents/")
        print("   The agent will still work using Gemini's general knowledge.")
        return None
    
    print(f"2. Creating vector store with {len(all_documents)} total chunks")
    vs_manager = VectorStoreManager()
    vectorstore = vs_manager.create_vectorstore(all_documents)
    
    print("\n✅ Vector store setup complete!")
    print(f"   Total documents: {len(all_documents)}")
    print(f"   Location: {vs_manager.persist_directory}")
    
    # Test the vector store
    print("\n3. Testing vector store with sample query...")
    test_results = vs_manager.similarity_search("How to write effective ad copy", k=2)
    print(f"   Found {len(test_results)} relevant documents")
    if test_results:
        print(f"   Sample: {test_results[0].page_content[:200]}...")
    
    return vs_manager


if __name__ == "__main__":
    # Create necessary directories
    os.makedirs("./data/documents", exist_ok=True)
    os.makedirs("./data/chroma_db", exist_ok=True)
    
    # Run setup
    setup_initial_vectorstore()