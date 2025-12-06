# Marketing AI Agent

An intelligent marketing assistant that combines **Agentic RAG** with **Knowledge Graph reasoning** to answer marketing questions and generate platform-optimized ad copy.

## Project Overview

This agent uses LangGraph for multi-step orchestration, integrating two complementary retrieval approaches: vector-based semantic search through ChromaDB for finding relevant marketing strategies from 1900+ indexed social media documents, and graph-based reasoning through NetworkX for enforcing platform-specific constraints like character limits, preferred tones, and CTAs.

The system supports multiple platforms including Facebook, Instagram, LinkedIn, TikTok, and Twitter, each with accurate 2024 character limits and best practices built into the knowledge graph.

## Architecture & Tools

| Component | Technology | Purpose |
|-----------|------------|---------|
| Agent Framework | LangGraph | 5-node workflow with conditional routing |
| LLM | Google Gemini 2.5 Flash | Text generation and analysis |
| Vector Store | ChromaDB | Semantic search with local embeddings |
| Embeddings | BAAI/bge-small-en-v1.5 | No API rate limits, runs locally |
| Knowledge Graph | NetworkX | 36 nodes, 67 edges (platforms, tones, CTAs) |
| API | FastAPI | REST backend with `/run-agent` endpoint |
| Memory | JSON-based | Stores feedback and successful patterns |

**Workflow:** The agent classifies queries into Q&A or optimization requests. Q&A queries follow: Classifier → Retriever → Generator. Optimization queries: Classifier → KG Query → Retriever → Copy Optimizer. The vector database provides "what works" while the knowledge graph provides "how to apply it."

## Features

- **Agentic RAG**: Multi-step reasoning with document retrieval
- **Knowledge Graph**: Platform constraints and relationships
- **Evaluation Metrics**: Relevance, hallucination rate, ROUGE, platform compliance
- **Learning System**: Stores high-rated patterns for improvement
- **Chat Interface**: Clean web UI with conversation memory

## Challenges & Solutions

1. **RAG + KG Integration**: Merged both systems in parallel, combining results in the optimizer node.
2. **Document Diversity**: Built unified ingestion with format-specific loaders (CSV, JSON, PDF).
3. **Character Limits**: Two-stage validation with regeneration on violations.
4. **Hallucination**: Fact-checking via regex extraction and source verification.

## Quick Start

```bash
pip install -r requirements.txt
echo "GOOGLE_API_KEY=your_key" > .env
python vectorstore_setup.py
python main.py
```

Open http://127.0.0.1:8000 to use the chat interface.

## Improvements & Next Steps

- Fine-tune on ad copywriting datasets
- Add multi-modal image analysis
- Integrate live campaign metrics via RLHF
- Scale with Redis caching and PostgreSQL

---


