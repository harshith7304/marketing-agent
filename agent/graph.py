"""
LangGraph Agent for Marketing Q&A and Ad Copy Optimization
"""

import os
from typing import TypedDict, List, Annotated, Optional
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from vectorstore_setup import VectorStoreManager
from knowledge_graph import MarketingKnowledgeGraph
from dotenv import load_dotenv
import operator

load_dotenv()


# Define the agent state
class AgentState(TypedDict):
    # Input
    query: str
    ad_text: Optional[str]
    target_platform: Optional[str]
    tone: Optional[str]
    industry: Optional[str]
    ad_type: Optional[str]
    
    # Intermediate states
    query_type: str  # "qa" or "optimize"
    retrieved_knowledge: List[str]
    platform_info: dict
    recommended_platforms: List[dict]
    
    # Output
    response: str
    optimized_copies: dict
    recommendations: List[str]
    
    # Memory/Feedback
    conversation_history: Annotated[List, operator.add]


class MarketingAgent:
    def __init__(self):
        # Initialize LLM (Gemini)
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",  # Fast and capable model
            temperature=0.7,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        
        # Initialize Vector Store
        self.vs_manager = VectorStoreManager()
        self.vectorstore_available = False
        try:
            self.vs_manager.load_vectorstore()
            self.vectorstore_available = True
        except (FileNotFoundError, Exception) as e:
            print(f"Vector store not available: {e}")
            print("Agent will use LLM general knowledge.")
        
        # Initialize Knowledge Graph
        self.kg = MarketingKnowledgeGraph()
        if os.path.exists("./data/marketing_kg.pickle"):
            self.kg.load()
        else:
            self.kg.save()
        
        # Build the agent graph
        self.agent = self._build_graph()
    
    def _build_graph(self):
        """Build the LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("classifier", self._classify_query)
        workflow.add_node("retriever", self._retrieve_knowledge)
        workflow.add_node("kg_query", self._query_knowledge_graph)
        workflow.add_node("qa_generator", self._generate_qa_response)
        workflow.add_node("copy_optimizer", self._optimize_copy)
        
        # Define edges
        workflow.set_entry_point("classifier")
        
        # Conditional routing based on query type after classifier
        workflow.add_conditional_edges(
            "classifier",
            self._route_by_query_type,
            {
                "qa": "retriever",
                "optimize": "kg_query"
            }
        )
        
        # Knowledge graph query leads to retriever
        workflow.add_edge("kg_query", "retriever")
        
        # Conditional routing after retriever based on query type
        workflow.add_conditional_edges(
            "retriever",
            self._route_after_retriever,
            {
                "qa": "qa_generator",
                "optimize": "copy_optimizer"
            }
        )
        
        # Final edges to END
        workflow.add_edge("qa_generator", END)
        workflow.add_edge("copy_optimizer", END)
        
        return workflow.compile()
    
    def _classify_query(self, state: AgentState) -> AgentState:
        """Classify whether this is a Q&A or optimization request"""
        query = state["query"].lower()
        ad_text = state.get("ad_text")
        
        # If ad_text is provided, it's definitely optimization
        if ad_text:
            state["query_type"] = "optimize"
        # Check for optimization keywords
        elif any(keyword in query for keyword in [
            "optimize", "rewrite", "improve", "create ad", "write copy", 
            "generate ad", "ad copy for", "make it", "change tone"
        ]):
            state["query_type"] = "optimize"
        else:
            state["query_type"] = "qa"
        
        return state
    
    def _route_by_query_type(self, state: AgentState) -> str:
        """Route to appropriate node based on query type"""
        return state["query_type"]
    
    def _route_after_retriever(self, state: AgentState) -> str:
        """Route after retriever based on query type"""
        return state["query_type"]
    
    def _retrieve_knowledge(self, state: AgentState) -> AgentState:
        """Retrieve relevant knowledge from vector store (RAG)"""
        query = state["query"]
        retrieved_docs = []
        
        # Only search if vector store is available
        if self.vectorstore_available:
            try:
                results = self.vs_manager.similarity_search(query, k=4)
                retrieved_docs = [doc.page_content for doc in results]
            except Exception as e:
                print(f"⚠️  Vector search failed: {e}")
        
        state["retrieved_knowledge"] = retrieved_docs
        return state
    
    def _query_knowledge_graph(self, state: AgentState) -> AgentState:
        """Query knowledge graph for platform info and recommendations"""
        target_platform = state.get("target_platform")
        industry = state.get("industry")
        ad_type = state.get("ad_type")
        
        # If no specific platform, find best platforms
        if not target_platform:
            recommended = self.kg.find_best_platforms(
                industry=industry,
                ad_type=ad_type
            )
            state["recommended_platforms"] = recommended[:3]  # Top 3
        else:
            # Get info for specific platform
            platform_info = self.kg.get_platform_info(target_platform)
            state["platform_info"] = platform_info
            state["recommended_platforms"] = [{"platform": target_platform, "score": 5}]
        
        return state
    
    def _generate_qa_response(self, state: AgentState) -> AgentState:
        """Generate response for Q&A queries"""
        query = state["query"]
        retrieved_knowledge = state.get("retrieved_knowledge", [])
        
        # Build prompt based on whether we have knowledge context
        if retrieved_knowledge:
            knowledge = "\n\n".join(retrieved_knowledge)
            prompt = f"""You are a marketing expert assistant. Answer the user's question based on the following knowledge base.

Knowledge Base:
{knowledge}

User Question: {query}

Provide a clear, concise, and actionable answer. If the knowledge base doesn't contain enough information, supplement with your general marketing expertise.

Answer:"""
        else:
            # No documents available - use general knowledge
            prompt = f"""You are a marketing expert assistant with deep knowledge of digital advertising, copywriting, and marketing best practices.

User Question: {query}

Provide a clear, concise, and actionable answer based on your marketing expertise and industry best practices.

Answer:"""
        
        messages = [
            SystemMessage(content="You are an expert marketing consultant specializing in digital advertising and copywriting."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        state["response"] = response.content
        
        # Add to conversation history
        state.setdefault("conversation_history", [])
        state["conversation_history"].append({
            "query": query,
            "response": response.content
        })
        
        return state
    
    def _optimize_copy(self, state: AgentState) -> AgentState:
        """Optimize ad copy for specified platforms"""
        query = state["query"]
        ad_text = state.get("ad_text", "")
        tone = state.get("tone", "professional")
        retrieved_knowledge = state.get("retrieved_knowledge", [])
        knowledge = "\n\n".join(retrieved_knowledge[:2]) if retrieved_knowledge else ""
        recommended_platforms = state.get("recommended_platforms", [])
        
        # Generate optimized copy for each recommended platform
        optimized_copies = {}
        recommendations = []
        
        for platform_data in recommended_platforms[:3]:  # Top 3 platforms
            platform = platform_data["platform"]
            platform_info = self.kg.get_platform_info(platform)
            
            if not platform_info:
                continue
            
            constraints = platform_info["constraints"]
            preferred_tones = platform_info["relationships"]["preferred_tones"]
            
            # Get recommended CTAs
            ad_type = state.get("ad_type", "Promotional")
            ctas = self.kg.get_recommended_cta(ad_type)
            
            # Build prompt with or without knowledge base context
            knowledge_section = f"\nBest Practices from Knowledge Base:\n{knowledge}\n" if knowledge else ""
            
            prompt = f"""You are an expert ad copywriter. Create optimized ad copy for {platform}.

Original Query/Request: {query}
Original Ad Text (if provided): {ad_text}
Desired Tone: {tone}

Platform: {platform}
Constraints:
- Character Limit: {constraints.get('char_limit') or constraints.get('headline_limit', 100)}
- Preferred Tones: {', '.join(preferred_tones)}
- Recommended CTAs: {', '.join(ctas[:3])}
{knowledge_section}
Create compelling ad copy that:
1. Follows the character limit strictly
2. Uses the {tone} tone but adapts to platform preferences
3. Includes a strong CTA
4. Is platform-appropriate

Provide ONLY the optimized ad copy, nothing else."""
            
            messages = [
                SystemMessage(content="You are an expert ad copywriter who creates compelling, platform-optimized ad copy."),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            optimized_copy = response.content.strip()
            
            # Validate length
            char_limit = constraints.get('char_limit') or constraints.get('headline_limit', 100)
            if len(optimized_copy) > char_limit:
                optimized_copy = optimized_copy[:char_limit-3] + "..."
            
            optimized_copies[platform] = {
                "copy": optimized_copy,
                "length": len(optimized_copy),
                "limit": char_limit,
                "recommended_ctas": ctas[:3],
                "preferred_tones": preferred_tones
            }
            
            # Generate platform-specific recommendations
            recommendations.append(
                f"**{platform}**: {len(optimized_copy)}/{char_limit} chars. "
                f"Best times: {constraints.get('best_time', 'N/A')}. "
                f"Avg CTR: {constraints.get('avg_ctr', 'N/A')}%"
            )
        
        state["optimized_copies"] = optimized_copies
        state["recommendations"] = recommendations
        
        # Create summary response
        summary = f"Generated optimized ad copy for {len(optimized_copies)} platforms based on your request.\n\n"
        for platform, data in optimized_copies.items():
            summary += f"**{platform}**:\n{data['copy']}\n\n"
        
        state["response"] = summary
        
        # Add to conversation history
        state.setdefault("conversation_history", [])
        state["conversation_history"].append({
            "query": query,
            "optimized_copies": optimized_copies
        })
        
        return state
    
    def run(self, query: str, ad_text: str = None, target_platform: str = None, 
            tone: str = "professional", industry: str = None, ad_type: str = "Promotional"):
        """Run the agent"""
        initial_state = {
            "query": query,
            "ad_text": ad_text,
            "target_platform": target_platform,
            "tone": tone,
            "industry": industry,
            "ad_type": ad_type,
            "conversation_history": []
        }
        
        result = self.agent.invoke(initial_state)
        return result


if __name__ == "__main__":
    # Test the agent
    agent = MarketingAgent()
    
    # Test 1: Q&A
    print("=== Test 1: Marketing Q&A ===")
    result = agent.run(query="What are the best practices for writing Facebook ad headlines?")
    print(result["response"])
    print("\n" + "="*50 + "\n")
    
    # Test 2: Ad Copy Optimization
    print("=== Test 2: Ad Copy Optimization ===")
    result = agent.run(
        query="Create ad copy for a summer sale",
        ad_text="Big summer sale! Save 50% on everything!",
        tone="urgent",
        industry="Ecommerce",
        ad_type="Promotional"
    )
    print(result["response"])
    print("\nRecommendations:")
    for rec in result["recommendations"]:
        print(f"  • {rec}")