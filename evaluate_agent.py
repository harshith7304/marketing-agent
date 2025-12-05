"""
Evaluate the Marketing AI Agent
Run this script to test all evaluation metrics
"""

from evaluation.metrics import AgentEvaluator
from knowledge_graph import MarketingKnowledgeGraph
from agent.graph import MarketingAgent
from agent.memory import AgentMemory
import json

print("=" * 60)
print("MARKETING AI AGENT - EVALUATION")
print("=" * 60)

# Initialize components
print("\nLoading agent...")
agent = MarketingAgent()
evaluator = AgentEvaluator()
kg = MarketingKnowledgeGraph()
memory = AgentMemory()

# Test cases
test_cases = [
    {
        "name": "Instagram Summer Sale",
        "query": "Create a summer sale ad for Instagram",
        "platform": "Instagram",
        "tone": "urgent"
    },
    {
        "name": "LinkedIn B2B Ad",
        "query": "Create a professional ad for LinkedIn targeting SaaS companies",
        "platform": "LinkedIn",
        "tone": "professional"
    },
    {
        "name": "TikTok Fitness App",
        "query": "Write a TikTok ad for a fitness app",
        "platform": "TikTok",
        "tone": "playful"
    }
]

print("\n" + "=" * 60)
print("RUNNING EVALUATIONS")
print("=" * 60)

results = []

for i, test in enumerate(test_cases, 1):
    print(f"\n--- Test {i}: {test['name']} ---")
    print(f"Query: {test['query']}")
    
    # Generate response
    result = agent.run(query=test['query'])
    response = result.get("response", "")
    
    # Get first 300 chars of response for display
    response_preview = response[:300] + "..." if len(response) > 300 else response
    print(f"Response: {response_preview}")
    
    # Get platform constraints
    platform_info = kg.get_platform_info(test['platform'])
    constraints = platform_info.get('constraints', {'char_limit': 280})
    
    # Evaluate
    evaluation = evaluator.comprehensive_evaluation(
        query=test['query'],
        generated_copy=response,
        platform=test['platform'],
        platform_constraints=constraints,
        target_tone=test['tone'],
        source_documents=result.get("retrieved_knowledge", [])
    )
    
    print(f"\nEVALUATION RESULTS:")
    print(f"  Overall Score: {evaluation['overall_score']}")
    print(f"  Grade: {evaluation['grade']}")
    print(f"  Platform Compliant: {evaluation['evaluations']['compliance']['compliant']}")
    print(f"  Character Count: {evaluation['evaluations']['compliance']['length']}/{constraints.get('char_limit', 'N/A')}")
    print(f"  Tone Match: {evaluation['evaluations']['tone_match']['match_score']}")
    print(f"  Has CTA: {evaluation['evaluations']['cta']['has_cta']}")
    
    if 'hallucination' in evaluation['evaluations']:
        print(f"  Hallucination Rate: {evaluation['evaluations']['hallucination']['hallucination_rate']}")
    
    results.append({
        "test": test['name'],
        "score": evaluation['overall_score'],
        "grade": evaluation['grade']
    })
    
    # Add as feedback (simulating user rating based on score)
    rating = 5 if evaluation['overall_score'] >= 0.8 else (4 if evaluation['overall_score'] >= 0.6 else 3)
    memory.add_feedback(
        query=test['query'],
        generated_copy=response[:500],
        platform=test['platform'],
        rating=rating,
        context={"tone": test['tone']}
    )

# Summary
print("\n" + "=" * 60)
print("EVALUATION SUMMARY")
print("=" * 60)

for r in results:
    print(f"  {r['test']}: {r['score']} ({r['grade']})")

avg_score = sum(r['score'] for r in results) / len(results)
print(f"\n  Average Score: {avg_score:.3f}")

# Learning insights
print("\n" + "=" * 60)
print("LEARNING INSIGHTS")
print("=" * 60)
insights = memory.analyze_learning_patterns()
for insight in insights:
    print(f"  • {insight}")

# Memory stats
print("\n" + "=" * 60)
print("MEMORY STATS")
print("=" * 60)
stats = memory.get_memory_stats()
print(f"  Successful Patterns Stored: {stats['successful_patterns']}")
print(f"  Total Feedback Received: {stats['total_feedback']}")
print(f"  Platforms Tracked: {stats['platforms_tracked']}")

print("\nEvaluation Complete.")
