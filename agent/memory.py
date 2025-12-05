"""
Memory and Learning System for the Agent
Stores feedback and learns from successful patterns
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from collections import defaultdict


class AgentMemory:
    def __init__(self, memory_file="./data/agent_memory.json"):
        self.memory_file = memory_file
        self.memory = self._load_memory()
    
    def _load_memory(self) -> dict:
        """Load memory from file"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading memory: {e}")
                return self._initialize_memory()
        return self._initialize_memory()
    
    def _initialize_memory(self) -> dict:
        """Initialize empty memory structure"""
        return {
            "user_preferences": {},
            "successful_patterns": [],
            "feedback_history": [],
            "platform_performance": defaultdict(list),
            "tone_effectiveness": defaultdict(list),
            "query_cache": {},
            "learning_insights": []
        }
    
    def save_memory(self):
        """Save memory to file"""
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        
        # Convert defaultdicts to regular dicts for JSON serialization
        memory_to_save = dict(self.memory)
        memory_to_save["platform_performance"] = dict(memory_to_save.get("platform_performance", {}))
        memory_to_save["tone_effectiveness"] = dict(memory_to_save.get("tone_effectiveness", {}))
        
        with open(self.memory_file, 'w') as f:
            json.dump(memory_to_save, f, indent=2)
    
    def add_user_preference(self, user_id: str, preference_key: str, preference_value: any):
        """Store user preferences"""
        if user_id not in self.memory["user_preferences"]:
            self.memory["user_preferences"][user_id] = {}
        
        self.memory["user_preferences"][user_id][preference_key] = preference_value
        self.save_memory()
    
    def get_user_preferences(self, user_id: str) -> dict:
        """Retrieve user preferences"""
        return self.memory["user_preferences"].get(user_id, {})
    
    def add_feedback(self, query: str, generated_copy: str, platform: str, 
                     rating: int, context: dict = None):
        """
        Store feedback for learning
        rating: 1-5 scale
        """
        feedback_entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "generated_copy": generated_copy,
            "platform": platform,
            "rating": rating,
            "context": context or {}
        }
        
        self.memory["feedback_history"].append(feedback_entry)
        
        # If highly rated (4-5), extract as successful pattern
        if rating >= 4:
            pattern = {
                "copy": generated_copy,
                "platform": platform,
                "context": context,
                "rating": rating,
                "timestamp": datetime.now().isoformat()
            }
            self.memory["successful_patterns"].append(pattern)
        
        # Track platform performance
        if "platform_performance" not in self.memory:
            self.memory["platform_performance"] = {}
        
        if platform not in self.memory["platform_performance"]:
            self.memory["platform_performance"][platform] = []
        
        self.memory["platform_performance"][platform].append(rating)
        
        # Track tone effectiveness if available
        if context and "tone" in context:
            tone = context["tone"]
            if "tone_effectiveness" not in self.memory:
                self.memory["tone_effectiveness"] = {}
            
            if tone not in self.memory["tone_effectiveness"]:
                self.memory["tone_effectiveness"][tone] = []
            
            self.memory["tone_effectiveness"][tone].append(rating)
        
        self.save_memory()
    
    def get_successful_patterns(self, platform: str = None, min_rating: int = 4) -> List[dict]:
        """Retrieve successful patterns, optionally filtered by platform"""
        patterns = self.memory["successful_patterns"]
        
        if platform:
            patterns = [p for p in patterns if p.get("platform") == platform]
        
        patterns = [p for p in patterns if p.get("rating", 0) >= min_rating]
        
        # Sort by rating (highest first)
        patterns.sort(key=lambda x: x.get("rating", 0), reverse=True)
        
        return patterns
    
    def get_platform_insights(self, platform: str) -> dict:
        """Get performance insights for a specific platform"""
        ratings = self.memory.get("platform_performance", {}).get(platform, [])
        
        if not ratings:
            return {
                "platform": platform,
                "avg_rating": None,
                "total_feedback": 0,
                "recommendation": "No data yet"
            }
        
        avg_rating = sum(ratings) / len(ratings)
        
        return {
            "platform": platform,
            "avg_rating": round(avg_rating, 2),
            "total_feedback": len(ratings),
            "recommendation": "Performing well" if avg_rating >= 4 else "Needs improvement"
        }
    
    def get_tone_insights(self, tone: str) -> dict:
        """Get effectiveness insights for a specific tone"""
        ratings = self.memory.get("tone_effectiveness", {}).get(tone, [])
        
        if not ratings:
            return {
                "tone": tone,
                "avg_rating": None,
                "total_usage": 0,
                "recommendation": "No data yet"
            }
        
        avg_rating = sum(ratings) / len(ratings)
        
        return {
            "tone": tone,
            "avg_rating": round(avg_rating, 2),
            "total_usage": len(ratings),
            "recommendation": "Effective" if avg_rating >= 4 else "Consider alternatives"
        }
    
    def analyze_learning_patterns(self):
        """Analyze feedback to extract learning insights"""
        insights = []
        
        # 1. Best performing platforms
        platform_perfs = {}
        for platform, ratings in self.memory.get("platform_performance", {}).items():
            if ratings:
                platform_perfs[platform] = sum(ratings) / len(ratings)
        
        if platform_perfs:
            best_platform = max(platform_perfs, key=platform_perfs.get)
            insights.append(f"Best performing platform: {best_platform} (avg rating: {platform_perfs[best_platform]:.2f})")
        
        # 2. Most effective tones
        tone_perfs = {}
        for tone, ratings in self.memory.get("tone_effectiveness", {}).items():
            if ratings:
                tone_perfs[tone] = sum(ratings) / len(ratings)
        
        if tone_perfs:
            best_tone = max(tone_perfs, key=tone_perfs.get)
            insights.append(f"Most effective tone: {best_tone} (avg rating: {tone_perfs[best_tone]:.2f})")
        
        # 3. Total feedback count
        total_feedback = len(self.memory.get("feedback_history", []))
        insights.append(f"Total feedback received: {total_feedback}")
        
        # 4. Success rate
        successful = len([f for f in self.memory.get("feedback_history", []) if f.get("rating", 0) >= 4])
        if total_feedback > 0:
            success_rate = (successful / total_feedback) * 100
            insights.append(f"Success rate (4+ stars): {success_rate:.1f}%")
        
        # Store insights
        self.memory["learning_insights"] = insights
        self.save_memory()
        
        return insights
    
    def get_recommendations_from_history(self, query: str, platform: str = None) -> List[str]:
        """Get recommendations based on similar past queries"""
        similar_patterns = []
        
        query_lower = query.lower()
        
        for pattern in self.memory["successful_patterns"]:
            # Simple keyword matching (can be improved with embeddings)
            pattern_context = str(pattern.get("context", {})).lower()
            
            if platform and pattern.get("platform") != platform:
                continue
            
            # Check if query keywords appear in successful pattern context
            keywords = query_lower.split()
            matches = sum(1 for keyword in keywords if keyword in pattern_context)
            
            if matches > 0:
                similar_patterns.append({
                    "pattern": pattern,
                    "relevance": matches
                })
        
        # Sort by relevance
        similar_patterns.sort(key=lambda x: x["relevance"], reverse=True)
        
        # Extract recommendations
        recommendations = []
        for item in similar_patterns[:3]:  # Top 3
            pattern = item["pattern"]
            recommendations.append(
                f"Based on past success: '{pattern['copy'][:100]}...' "
                f"(rated {pattern['rating']}/5 for {pattern['platform']})"
            )
        
        return recommendations
    
    def cache_query_response(self, query: str, response: str):
        """Cache query-response pairs to avoid redundant processing"""
        cache_key = query.lower().strip()
        self.memory["query_cache"][cache_key] = {
            "response": response,
            "timestamp": datetime.now().isoformat()
        }
        
        # Keep cache limited to last 100 entries
        if len(self.memory["query_cache"]) > 100:
            # Remove oldest entries
            sorted_cache = sorted(
                self.memory["query_cache"].items(),
                key=lambda x: x[1]["timestamp"]
            )
            self.memory["query_cache"] = dict(sorted_cache[-100:])
        
        self.save_memory()
    
    def get_cached_response(self, query: str) -> Optional[str]:
        """Retrieve cached response if available"""
        cache_key = query.lower().strip()
        cached = self.memory["query_cache"].get(cache_key)
        
        if cached:
            return cached["response"]
        
        return None
    
    def get_memory_stats(self) -> dict:
        """Get overall memory statistics"""
        return {
            "total_users": len(self.memory.get("user_preferences", {})),
            "successful_patterns": len(self.memory.get("successful_patterns", [])),
            "total_feedback": len(self.memory.get("feedback_history", [])),
            "platforms_tracked": len(self.memory.get("platform_performance", {})),
            "tones_tracked": len(self.memory.get("tone_effectiveness", {})),
            "cached_queries": len(self.memory.get("query_cache", {})),
            "learning_insights": self.memory.get("learning_insights", [])
        }


if __name__ == "__main__":
    # Test the memory system
    memory = AgentMemory()
    
    # Add some test feedback
    memory.add_feedback(
        query="Create summer sale ad",
        generated_copy="☀️ Summer Sale! Save 50% on everything. Shop now!",
        platform="Facebook",
        rating=5,
        context={"tone": "urgent", "industry": "Ecommerce"}
    )
    
    memory.add_feedback(
        query="LinkedIn B2B ad",
        generated_copy="Streamline your workflow with our enterprise solution. Learn more.",
        platform="LinkedIn",
        rating=4,
        context={"tone": "professional", "industry": "SaaS"}
    )
    
    # Get insights
    print("=== Memory Statistics ===")
    print(json.dumps(memory.get_memory_stats(), indent=2))
    
    print("\n=== Platform Insights ===")
    print(json.dumps(memory.get_platform_insights("Facebook"), indent=2))
    
    print("\n=== Learning Patterns ===")
    insights = memory.analyze_learning_patterns()
    for insight in insights:
        print(f"  • {insight}")
    
    print("\n=== Successful Patterns ===")
    patterns = memory.get_successful_patterns(min_rating=4)
    for pattern in patterns:
        print(f"  • {pattern['platform']}: {pattern['copy'][:80]}...")