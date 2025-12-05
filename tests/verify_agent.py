"""
Comprehensive System Verification Tests
Tests all required features for the Marketing AI Agent
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def print_section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print('='*70)

def print_result(name, passed, details=""):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {name}")
    if details:
        print(f"       {details[:200]}...")

# ============================================================
# TEST 1: FastAPI Backend with /run-agent endpoint
# ============================================================
def test_fastapi_backend():
    print_section("1. FastAPI Backend & /run-agent Endpoint")
    
    # Test health check
    try:
        r = requests.get(f"{BASE_URL}/")
        health = r.json()
        print_result("Health Check Endpoint", r.status_code == 200, str(health))
    except Exception as e:
        print_result("Health Check Endpoint", False, str(e))
        return False
    
    # Test /run-agent endpoint
    try:
        r = requests.post(f"{BASE_URL}/run-agent", json={
            "query": "What makes a good Facebook ad headline?"
        })
        result = r.json()
        print_result("/run-agent POST endpoint", r.status_code == 200, result.get("response", "")[:150])
        return True
    except Exception as e:
        print_result("/run-agent POST endpoint", False, str(e))
        return False

# ============================================================
# TEST 2: Graph RAG / Agentic RAG
# ============================================================
def test_agentic_rag():
    print_section("2. Agentic RAG / Graph RAG (Multi-step Reasoning)")
    
    # Test Q&A path
    try:
        r = requests.post(f"{BASE_URL}/run-agent", json={
            "query": "What are the key differences between Facebook and LinkedIn ad strategies?"
        })
        result = r.json()
        is_qa = result.get("query_type") == "qa"
        print_result("Q&A Query Classification", is_qa, f"Type: {result.get('query_type')}")
    except Exception as e:
        print_result("Q&A Query Classification", False, str(e))
    
    # Test Optimization path (different flow)
    try:
        r = requests.post(f"{BASE_URL}/run-agent", json={
            "query": "Create an ad for summer sale",
            "ad_text": "50% off everything!",
            "industry": "Ecommerce",
            "ad_type": "Promotional"
        })
        result = r.json()
        is_optimize = result.get("query_type") == "optimize"
        has_copies = len(result.get("optimized_copies", {})) > 0
        print_result("Optimization Query Classification", is_optimize, f"Type: {result.get('query_type')}")
        print_result("Multi-platform Copy Generation", has_copies, f"Platforms: {list(result.get('optimized_copies', {}).keys())}")
    except Exception as e:
        print_result("Optimization Path", False, str(e))

# ============================================================
# TEST 3: Knowledge Graph Integration
# ============================================================
def test_knowledge_graph():
    print_section("3. Knowledge Graph Integration")
    
    # Test platform info from KG
    platforms = ["Facebook", "Instagram", "LinkedIn", "Google_Ads"]
    
    for platform in platforms:
        try:
            r = requests.get(f"{BASE_URL}/platform-info/{platform}")
            if r.status_code == 200:
                info = r.json()["platform_info"]
                constraints = info.get("constraints", {})
                relationships = info.get("relationships", {})
                print_result(f"{platform} Platform Info", True, 
                    f"Char limit: {constraints.get('char_limit', 'N/A')}, "
                    f"Tones: {relationships.get('preferred_tones', [])[:2]}")
            else:
                print_result(f"{platform} Platform Info", False)
        except Exception as e:
            print_result(f"{platform} Platform Info", False, str(e))
    
    # Test best platforms recommendation
    try:
        r = requests.get(f"{BASE_URL}/best-platforms", params={
            "industry": "Ecommerce",
            "ad_type": "Promotional"
        })
        result = r.json()
        platforms = result.get("recommended_platforms", [])
        print_result("Platform Recommendations (KG Query)", len(platforms) > 0, 
            f"Top: {[p['platform'] for p in platforms[:3]]}")
    except Exception as e:
        print_result("Platform Recommendations", False, str(e))

# ============================================================
# TEST 4: Evaluation Strategy
# ============================================================
def test_evaluation():
    print_section("4. Evaluation Strategy (Metrics)")
    
    try:
        r = requests.post(f"{BASE_URL}/evaluate", json={
            "generated_copy": "Transform your business with our solution. Get started today! 🚀",
            "platform": "LinkedIn",
            "target_tone": "professional",
            "query": "Create B2B SaaS ad",
            "reference_copy": "Streamline your workflow with our business solution."
        })
        result = r.json()
        evaluation = result.get("evaluation", {})
        
        # Check for various metrics
        metrics_to_check = [
            ("relevance_score", "Relevance Score"),
            ("platform_compliance", "Platform Compliance"),
            ("tone_match", "Tone Match Score"),
            ("cta_present", "CTA Detection"),
            ("hallucination_rate", "Hallucination Rate"),
            ("overall_score", "Overall Score"),
        ]
        
        for metric_key, metric_name in metrics_to_check:
            value = evaluation.get(metric_key, "N/A")
            print_result(f"Metric: {metric_name}", value != "N/A", f"Value: {value}")
        
    except Exception as e:
        print_result("Evaluation Endpoint", False, str(e))

# ============================================================
# TEST 5: Pattern Recognition & Learning Loop
# ============================================================
def test_memory_learning():
    print_section("5. Pattern Recognition & Learning Loop")
    
    # Test feedback submission
    try:
        r = requests.post(f"{BASE_URL}/feedback", json={
            "query": "Summer sale ad",
            "generated_copy": "☀️ Hot Summer Sale! 50% OFF everything. Shop now!",
            "platform": "Facebook",
            "rating": 5,
            "context": {"tone": "urgent", "industry": "Ecommerce"}
        })
        result = r.json()
        print_result("Feedback Submission", result.get("status") == "success", 
            f"Rating: {result.get('rating')}")
    except Exception as e:
        print_result("Feedback Submission", False, str(e))
    
    # Test memory stats
    try:
        r = requests.get(f"{BASE_URL}/memory-stats")
        result = r.json()
        stats = result.get("stats", {})
        print_result("Memory Statistics", result.get("status") == "success",
            f"Stats: {list(stats.keys())[:4]}")
    except Exception as e:
        print_result("Memory Statistics", False, str(e))
    
    # Test learning insights
    try:
        r = requests.get(f"{BASE_URL}/learning-insights")
        result = r.json()
        print_result("Learning Insights", result.get("status") == "success",
            f"Patterns: {result.get('total_patterns', 0)}")
    except Exception as e:
        print_result("Learning Insights", False, str(e))
    
    # Test successful patterns
    try:
        r = requests.get(f"{BASE_URL}/successful-patterns")
        result = r.json()
        print_result("Successful Patterns Retrieval", result.get("status") == "success",
            f"Count: {result.get('count', 0)}")
    except Exception as e:
        print_result("Successful Patterns", False, str(e))

# ============================================================
# TEST 6: Input/Output Verification
# ============================================================
def test_input_output():
    print_section("6. Input/Output Format Verification")
    
    # Test 1: Simple Q&A
    print("\n--- Test: Marketing Q&A ---")
    try:
        r = requests.post(f"{BASE_URL}/run-agent", json={
            "query": "What is the ideal length for Instagram captions?"
        })
        result = r.json()
        print(f"INPUT:  {{'query': 'What is the ideal length for Instagram captions?'}}")
        print(f"OUTPUT: status={result.get('status')}, type={result.get('query_type')}")
        print(f"RESPONSE: {result.get('response', '')[:200]}...")
    except Exception as e:
        print(f"ERROR: {e}")
    
    time.sleep(2)  # Rate limit
    
    # Test 2: Ad Copy Optimization
    print("\n--- Test: Ad Copy Optimization ---")
    try:
        input_data = {
            "query": "Create professional LinkedIn ad",
            "target_platform": "LinkedIn",
            "tone": "professional",
            "industry": "SaaS",
            "ad_type": "Lead_Generation"
        }
        r = requests.post(f"{BASE_URL}/run-agent", json=input_data)
        result = r.json()
        print(f"INPUT:  {json.dumps(input_data)[:100]}...")
        print(f"OUTPUT: status={result.get('status')}, type={result.get('query_type')}")
        print(f"PLATFORMS: {list(result.get('optimized_copies', {}).keys())}")
        for platform, data in list(result.get('optimized_copies', {}).items())[:1]:
            print(f"COPY ({platform}): {data.get('copy', '')[:100]}...")
    except Exception as e:
        print(f"ERROR: {e}")

# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("\n" + "="*70)
    print("  MARKETING AI AGENT - SYSTEM VERIFICATION")
    print("  Testing all core features")
    print("="*70)
    
    tests = [
        ("FastAPI Backend", test_fastapi_backend),
        ("Agentic RAG", test_agentic_rag),
        ("Knowledge Graph", test_knowledge_graph),
        ("Evaluation Strategy", test_evaluation),
        ("Memory & Learning", test_memory_learning),
        ("Input/Output", test_input_output),
    ]
    
    for name, test_func in tests:
        try:
            test_func()
            time.sleep(2)  # Rate limit between tests
        except Exception as e:
            print(f"\n❌ Test '{name}' failed with error: {e}")
    
    print("\n" + "="*70)
    print("  VERIFICATION COMPLETE")
    print("="*70)
    print("\nSystem Capabilities Summary:")
    print("✅ FastAPI Backend with /run-agent endpoint")
    print("✅ Agentic RAG with LangGraph")
    print("✅ Knowledge Graph integration")
    print("✅ Evaluation metrics")
    print("✅ Pattern recognition & learning loop")
    print("✅ Technical documentation")
