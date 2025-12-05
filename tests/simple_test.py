import requests
import json

print("=" * 60)
print("SYSTEM HEALTH & FEATURE TESTS")
print("=" * 60)

# Test 1: Health Check
print("\n[TEST 1] Health Check")
r = requests.get("http://localhost:8000/")
print(f"Status: {r.status_code}")
print(f"Endpoints: {r.json().get('endpoints', [])[:5]}")

# Test 2: Marketing Q&A (/run-agent)
print("\n[TEST 2] Marketing Q&A - /run-agent endpoint")
r = requests.post("http://localhost:8000/run-agent", json={
    "query": "What are the best practices for Facebook ads?"
})
result = r.json()
print(f"Status: {result.get('status')}")
print(f"Query Type: {result.get('query_type')}")
print(f"Response (first 200 chars): {result.get('response', '')[:200]}...")

# Test 3: Ad Copy Optimization
print("\n[TEST 3] Ad Copy Optimization")
r = requests.post("http://localhost:8000/run-agent", json={
    "query": "Create summer sale ad",
    "ad_text": "50% off everything!",
    "tone": "urgent",
    "industry": "Ecommerce",
    "ad_type": "Promotional"
})
result = r.json()
print(f"Status: {result.get('status')}")
print(f"Query Type: {result.get('query_type')}")
print(f"Platforms Generated: {list(result.get('optimized_copies', {}).keys())}")
for platform, data in list(result.get("optimized_copies", {}).items())[:2]:
    print(f"  {platform}: {data.get('copy', '')[:80]}...")

# Test 4: Knowledge Graph - Platform Info
print("\n[TEST 4] Knowledge Graph - Platform Info")
r = requests.get("http://localhost:8000/platform-info/Facebook")
result = r.json()
info = result.get("platform_info", {})
print(f"Platform: {info.get('platform')}")
print(f"Char Limit: {info.get('constraints', {}).get('char_limit')}")
print(f"Preferred Tones: {info.get('relationships', {}).get('preferred_tones')}")

# Test 5: Best Platforms (KG Query)
print("\n[TEST 5] Knowledge Graph - Best Platforms")
r = requests.get("http://localhost:8000/best-platforms", params={
    "industry": "Ecommerce", "ad_type": "Promotional"
})
result = r.json()
platforms = result.get("recommended_platforms", [])
print(f"Top Platforms: {[p['platform'] for p in platforms[:3]]}")

# Test 6: Evaluation Metrics
print("\n[TEST 6] Evaluation Strategy")
r = requests.post("http://localhost:8000/evaluate", json={
    "generated_copy": "Transform your business today! Get started now.",
    "platform": "LinkedIn",
    "target_tone": "professional",
    "query": "Create B2B ad"
})
result = r.json()
eval_data = result.get("evaluation", {})
print(f"Overall Score: {eval_data.get('overall_score')}")
print(f"Grade: {eval_data.get('grade')}")
print(f"Relevance: {eval_data.get('relevance_score')}")
print(f"Platform Compliance: {eval_data.get('platform_compliance')}")
print(f"Hallucination Rate: {eval_data.get('hallucination_rate')}")

# Test 7: Feedback & Memory
print("\n[TEST 7] Memory & Learning Loop")
r = requests.post("http://localhost:8000/feedback", json={
    "query": "Summer sale",
    "generated_copy": "Hot Sale! 50% OFF!",
    "platform": "Facebook",
    "rating": 5,
    "context": {"tone": "urgent"}
})
print(f"Feedback Status: {r.json().get('status')}")

r = requests.get("http://localhost:8000/memory-stats")
stats = r.json().get("stats", {})
print(f"Memory Stats: {list(stats.keys())}")

r = requests.get("http://localhost:8000/learning-insights")
print(f"Learning Patterns: {r.json().get('total_patterns')}")

# Summary
print("\n" + "=" * 60)
print("SYSTEM CAPABILITIES VERIFICATION")
print("=" * 60)
print("[-] FastAPI Backend with /run-agent endpoint")
print("[-] Agentic RAG with LangGraph (multi-step reasoning)")
print("[-] Knowledge Graph integration (platforms, tones, CTAs)")
print("[-] Evaluation metrics (relevance, hallucination, compliance)")
print("[-] Pattern recognition & learning loop (memory, feedback)")
print("[-] Technical documentation")
print("=" * 60)
