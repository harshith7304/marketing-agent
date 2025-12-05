"""
Test Script for Marketing Agent
Run this to test all functionality
"""

import requests
import json
import time


BASE_URL = "http://localhost:8000"


def print_response(title, response):
    """Pretty print API response"""
    print(f"\n{'='*60}")
    print(f"📊 {title}")
    print('='*60)
    print(json.dumps(response, indent=2))
    print()


def test_health_check():
    """Test health check endpoint"""
    print("\n🏥 Testing Health Check...")
    response = requests.get(f"{BASE_URL}/")
    print_response("Health Check", response.json())
    return response.status_code == 200


def test_marketing_qa():
    """Test marketing Q&A functionality"""
    print("\n💬 Testing Marketing Q&A...")
    
    data = {
        "query": "What are the best practices for writing effective Facebook ad headlines?"
    }
    
    response = requests.post(f"{BASE_URL}/run-agent", json=data)
    print_response("Marketing Q&A Response", response.json())
    return response.status_code == 200


def test_ad_copy_optimization():
    """Test ad copy optimization"""
    print("\n✨ Testing Ad Copy Optimization...")
    
    data = {
        "query": "Create compelling ad copy for a summer sale campaign",
        "ad_text": "Big summer sale! Save 50% on everything in store!",
        "tone": "urgent",
        "industry": "Ecommerce",
        "ad_type": "Promotional"
    }
    
    response = requests.post(f"{BASE_URL}/run-agent", json=data)
    result = response.json()
    print_response("Ad Copy Optimization", result)
    
    # Show each platform's copy
    if "optimized_copies" in result:
        print("\n📝 Generated Copies:")
        for platform, data in result["optimized_copies"].items():
            print(f"\n{platform}:")
            print(f"  Copy: {data['copy']}")
            print(f"  Length: {data['length']}/{data['limit']} chars")
    
    return response.status_code == 200


def test_platform_specific_optimization():
    """Test platform-specific optimization"""
    print("\n🎯 Testing Platform-Specific Optimization...")
    
    data = {
        "query": "Create professional LinkedIn ad for B2B SaaS product",
        "target_platform": "LinkedIn",
        "tone": "professional",
        "industry": "SaaS",
        "ad_type": "Lead_Generation"
    }
    
    response = requests.post(f"{BASE_URL}/optimize-copy", json=data)
    print_response("LinkedIn-Specific Copy", response.json())
    return response.status_code == 200


def test_knowledge_query():
    """Test knowledge base query"""
    print("\n📚 Testing Knowledge Query...")
    
    data = {
        "query": "What makes a good call-to-action in digital ads?"
    }
    
    response = requests.post(f"{BASE_URL}/knowledge-query", json=data)
    print_response("Knowledge Query Response", response.json())
    return response.status_code == 200


def test_platform_info():
    """Test platform information retrieval"""
    print("\n📱 Testing Platform Info Retrieval...")
    
    platforms = ["Facebook", "Instagram", "Google_Ads", "LinkedIn"]
    
    for platform in platforms:
        response = requests.get(f"{BASE_URL}/platform-info/{platform}")
        if response.status_code == 200:
            print(f"\n✓ {platform}: OK")
        else:
            print(f"\n✗ {platform}: Failed")
    
    # Show detailed info for Facebook
    response = requests.get(f"{BASE_URL}/platform-info/Facebook")
    print_response("Facebook Platform Info", response.json())
    return response.status_code == 200


def test_feedback_submission():
    """Test feedback submission"""
    print("\n💯 Testing Feedback Submission...")
    
    data = {
        "query": "Summer sale ad",
        "generated_copy": "☀️ Summer Sale! Save 50% on everything. Shop now!",
        "platform": "Facebook",
        "rating": 5,
        "context": {
            "tone": "urgent",
            "industry": "Ecommerce"
        }
    }
    
    response = requests.post(f"{BASE_URL}/feedback", json=data)
    print_response("Feedback Submission", response.json())
    return response.status_code == 200


def test_evaluation():
    """Test copy evaluation"""
    print("\n📊 Testing Copy Evaluation...")
    
    data = {
        "generated_copy": "Transform your business with our enterprise solution. Get started today!",
        "platform": "LinkedIn",
        "target_tone": "professional",
        "query": "Create B2B SaaS ad",
        "reference_copy": "Streamline your workflow with our business solution. Learn more."
    }
    
    response = requests.post(f"{BASE_URL}/evaluate", json=data)
    result = response.json()
    print_response("Evaluation Results", result)
    
    if "evaluation" in result:
        eval_data = result["evaluation"]
        print(f"\n📈 Overall Score: {eval_data.get('overall_score')} ({eval_data.get('grade')})")
    
    return response.status_code == 200


def test_memory_stats():
    """Test memory statistics"""
    print("\n🧠 Testing Memory Stats...")
    
    response = requests.get(f"{BASE_URL}/memory-stats")
    print_response("Memory Statistics", response.json())
    return response.status_code == 200


def test_learning_insights():
    """Test learning insights"""
    print("\n💡 Testing Learning Insights...")
    
    response = requests.get(f"{BASE_URL}/learning-insights")
    result = response.json()
    print_response("Learning Insights", result)
    
    if "insights" in result:
        print("\n🔍 Key Insights:")
        for insight in result["insights"]:
            print(f"  • {insight}")
    
    return response.status_code == 200


def test_best_platforms():
    """Test best platform recommendations"""
    print("\n🎯 Testing Platform Recommendations...")
    
    response = requests.get(
        f"{BASE_URL}/best-platforms",
        params={"industry": "Ecommerce", "ad_type": "Promotional"}
    )
    print_response("Recommended Platforms", response.json())
    return response.status_code == 200


def test_successful_patterns():
    """Test successful patterns retrieval"""
    print("\n⭐ Testing Successful Patterns...")
    
    response = requests.get(f"{BASE_URL}/successful-patterns")
    print_response("Successful Patterns", response.json())
    return response.status_code == 200


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 MARKETING AI AGENT - TEST SUITE")
    print("="*60)
    
    tests = [
        ("Health Check", test_health_check),
        ("Marketing Q&A", test_marketing_qa),
        ("Ad Copy Optimization", test_ad_copy_optimization),
        ("Platform-Specific Optimization", test_platform_specific_optimization),
        ("Knowledge Query", test_knowledge_query),
        ("Platform Info", test_platform_info),
        ("Feedback Submission", test_feedback_submission),
        ("Copy Evaluation", test_evaluation),
        ("Memory Stats", test_memory_stats),
        ("Learning Insights", test_learning_insights),
        ("Platform Recommendations", test_best_platforms),
        ("Successful Patterns", test_successful_patterns),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            time.sleep(1)  # Small delay between tests
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n❌ {test_name} failed with error: {str(e)}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "="*60)
    print("📋 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print("\n" + "="*60)
    print(f"Result: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    print("="*60 + "\n")
    
    return passed == total


if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║          MARKETING AI AGENT - TEST SUITE                  ║
    ╚═══════════════════════════════════════════════════════════╝
    
    Make sure the API is running on http://localhost:8000
    
    Start the API with: python main.py
    
    Press Enter to start testing...
    """)
    
    input()
    
    try:
        success = run_all_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ Test suite failed: {str(e)}")
        exit(1)