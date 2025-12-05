"""
Knowledge Graph for Marketing Platforms and Ad Copy Optimization
"""

import networkx as nx
import json
import os
import pickle


class MarketingKnowledgeGraph:
    def __init__(self):
        self.graph = nx.DiGraph()
        self._build_graph()
    
    def _build_graph(self):
        """Build the marketing knowledge graph"""
        
        # 1. PLATFORMS (Correct 2024 character limits from official sources)
        platforms = {
            "Facebook": {
                "char_limit": 125,           # Primary text (recommended, visible)
                "headline_limit": 40,        # Headline
                "description_limit": 30,     # Link description
                "hashtag_limit": 3,
                "best_time": "1-3pm",
                "avg_ctr": 0.9
            },
            "Instagram": {
                "char_limit": 125,           # Visible before "...more" (optimal for ads)
                "char_limit_max": 2200,      # Max if needed
                "headline_limit": 40,        # Ad headline
                "hashtag_limit": 30,         # Max hashtags
                "hashtag_optimal": 5,        # Recommended for ads
                "best_time": "11am-1pm",
                "avg_ctr": 1.08,
                "focus": "visual"            # Visual-first platform
            },
            "Google_Ads": {
                "headline_limit": 30,        # Per headline (3 headlines)
                "description_limit": 90,     # Per description (2 descriptions)
                "headline_count": 3,
                "description_count": 2,
                "best_time": "business_hours",
                "avg_ctr": 3.17
            },
            "LinkedIn": {
                "char_limit": 150,           # Intro text (visible on mobile)
                "char_limit_max": 600,       # Max intro text
                "headline_limit": 70,        # Recommended (200 max)
                "description_limit": 300,    # Max description
                "best_time": "7-8am, 5-6pm",
                "avg_ctr": 0.65,
                "focus": "text"              # Text-heavy, B2B platform
            },
            "Twitter": {
                "char_limit": 280,           # Tweet max
                "optimal_length": 100,       # Recommended for engagement
                "hashtag_limit": 2,
                "best_time": "12-3pm",
                "avg_ctr": 1.55
            },
            "TikTok": {
                "caption_limit": 100,        # Recommended for ads (visible)
                "caption_max": 2200,         # Max for Spark Ads
                "hashtag_limit": 5,
                "best_time": "7-9am, 7-11pm",
                "avg_ctr": 2.5,
                "focus": "visual"            # Video-first, short captions
            }
        }
        
        for platform, attrs in platforms.items():
            self.graph.add_node(platform, type="platform", **attrs)
        
        # 2. TONES
        tones = {
            "Professional": {"formality": "high", "emotion": "low"},
            "Casual": {"formality": "low", "emotion": "medium"},
            "Urgent": {"formality": "medium", "emotion": "high"},
            "Playful": {"formality": "low", "emotion": "high"},
            "Informative": {"formality": "high", "emotion": "low"},
            "Conversational": {"formality": "low", "emotion": "medium"},
            "Authoritative": {"formality": "high", "emotion": "low"},
            "Friendly": {"formality": "low", "emotion": "medium"}
        }
        
        for tone, attrs in tones.items():
            self.graph.add_node(tone, type="tone", **attrs)
        
        # 3. AD TYPES
        ad_types = {
            "Promotional": {"goal": "sales", "urgency": "high"},
            "Awareness": {"goal": "reach", "urgency": "low"},
            "Engagement": {"goal": "interaction", "urgency": "medium"},
            "Educational": {"goal": "inform", "urgency": "low"},
            "Retargeting": {"goal": "conversion", "urgency": "high"},
            "Lead_Generation": {"goal": "leads", "urgency": "medium"}
        }
        
        for ad_type, attrs in ad_types.items():
            self.graph.add_node(ad_type, type="ad_type", **attrs)
        
        # 4. INDUSTRIES
        industries = [
            "Ecommerce", "SaaS", "Healthcare", "Finance", 
            "Education", "Real_Estate", "Travel", "Food"
        ]
        
        for industry in industries:
            self.graph.add_node(industry, type="industry")
        
        # 5. CTA TYPES
        cta_types = [
            "Shop_Now", "Learn_More", "Sign_Up", "Get_Started",
            "Download", "Book_Now", "Try_Free", "Contact_Us"
        ]
        
        for cta in cta_types:
            self.graph.add_node(cta, type="cta")
        
        # 6. CREATE RELATIONSHIPS
        
        # Platform -> Tone preferences
        tone_preferences = {
            "Facebook": ["Casual", "Friendly", "Conversational"],
            "Instagram": ["Playful", "Casual", "Friendly"],
            "Google_Ads": ["Urgent", "Informative", "Professional"],
            "LinkedIn": ["Professional", "Authoritative", "Informative"],
            "Twitter": ["Conversational", "Casual", "Playful"],
            "TikTok": ["Playful", "Casual", "Urgent"]
        }
        
        for platform, tones in tone_preferences.items():
            for tone in tones:
                self.graph.add_edge(platform, tone, relationship="prefers_tone")
        
        # Platform -> Ad Type effectiveness
        ad_type_effectiveness = {
            "Facebook": ["Promotional", "Engagement", "Retargeting"],
            "Instagram": ["Awareness", "Engagement", "Promotional"],
            "Google_Ads": ["Promotional", "Lead_Generation", "Retargeting"],
            "LinkedIn": ["Lead_Generation", "Educational", "Awareness"],
            "Twitter": ["Awareness", "Engagement", "Educational"],
            "TikTok": ["Awareness", "Engagement", "Promotional"]
        }
        
        for platform, ad_types in ad_type_effectiveness.items():
            for ad_type in ad_types:
                self.graph.add_edge(platform, ad_type, relationship="effective_for")
        
        # Platform -> Industry fit
        industry_fit = {
            "Facebook": ["Ecommerce", "Travel", "Food", "Real_Estate"],
            "Instagram": ["Ecommerce", "Travel", "Food", "Fashion"],
            "Google_Ads": ["SaaS", "Finance", "Healthcare", "Education"],
            "LinkedIn": ["SaaS", "Finance", "Education", "Healthcare"],
            "Twitter": ["SaaS", "Education", "News", "Tech"],
            "TikTok": ["Ecommerce", "Food", "Entertainment", "Fashion"]
        }
        
        for platform, industries in industry_fit.items():
            for industry in industries:
                if industry in self.graph.nodes():
                    self.graph.add_edge(platform, industry, relationship="strong_for")
        
        # Ad Type -> CTA mapping
        cta_mapping = {
            "Promotional": ["Shop_Now", "Get_Started", "Try_Free"],
            "Lead_Generation": ["Sign_Up", "Contact_Us", "Learn_More"],
            "Educational": ["Learn_More", "Download", "Sign_Up"],
            "Retargeting": ["Shop_Now", "Book_Now", "Try_Free"]
        }
        
        for ad_type, ctas in cta_mapping.items():
            for cta in ctas:
                self.graph.add_edge(ad_type, cta, relationship="uses_cta")
    
    def get_platform_info(self, platform: str):
        """Get all information about a platform"""
        if platform not in self.graph.nodes():
            return None
        
        node_data = dict(self.graph.nodes[platform])
        
        # Get connected nodes
        neighbors = {
            "preferred_tones": [],
            "effective_ad_types": [],
            "strong_industries": [],
        }
        
        for neighbor in self.graph.neighbors(platform):
            edge_data = self.graph.get_edge_data(platform, neighbor)
            relationship = edge_data.get("relationship", "")
            
            if relationship == "prefers_tone":
                neighbors["preferred_tones"].append(neighbor)
            elif relationship == "effective_for":
                neighbors["effective_ad_types"].append(neighbor)
            elif relationship == "strong_for":
                neighbors["strong_industries"].append(neighbor)
        
        return {
            "platform": platform,
            "constraints": node_data,
            "relationships": neighbors
        }
    
    def get_recommended_cta(self, ad_type: str):
        """Get recommended CTAs for an ad type"""
        ctas = []
        if ad_type in self.graph.nodes():
            for neighbor in self.graph.neighbors(ad_type):
                edge_data = self.graph.get_edge_data(ad_type, neighbor)
                if edge_data.get("relationship") == "uses_cta":
                    ctas.append(neighbor)
        return ctas
    
    def find_best_platforms(self, industry: str = None, ad_type: str = None):
        """Find best platforms based on industry and ad type"""
        suitable_platforms = []
        
        for node in self.graph.nodes():
            if self.graph.nodes[node].get("type") == "platform":
                score = 0
                
                if industry:
                    # Check if platform is strong for this industry
                    if self.graph.has_edge(node, industry):
                        edge_data = self.graph.get_edge_data(node, industry)
                        if edge_data.get("relationship") == "strong_for":
                            score += 2
                
                if ad_type:
                    # Check if platform is effective for this ad type
                    if self.graph.has_edge(node, ad_type):
                        edge_data = self.graph.get_edge_data(node, ad_type)
                        if edge_data.get("relationship") == "effective_for":
                            score += 2
                
                if score > 0:
                    suitable_platforms.append({
                        "platform": node,
                        "score": score
                    })
        
        # Sort by score
        suitable_platforms.sort(key=lambda x: x["score"], reverse=True)
        return suitable_platforms
    
    def save(self, file_path="./data/marketing_kg.pickle"):
        """Save knowledge graph to file"""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'wb') as f:
            pickle.dump(self.graph, f)
        print(f"Knowledge graph saved to {file_path}")
    
    def load(self, file_path="./data/marketing_kg.pickle"):
        """Load knowledge graph from file"""
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                self.graph = pickle.load(f)
            print(f"Knowledge graph loaded from {file_path}")
        else:
            print(f"No existing graph found. Building new one.")
            self._build_graph()
    
    def get_graph_summary(self):
        """Get summary statistics of the graph"""
        return {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "node_types": {
                "platforms": len([n for n in self.graph.nodes() if self.graph.nodes[n].get("type") == "platform"]),
                "tones": len([n for n in self.graph.nodes() if self.graph.nodes[n].get("type") == "tone"]),
                "ad_types": len([n for n in self.graph.nodes() if self.graph.nodes[n].get("type") == "ad_type"]),
                "industries": len([n for n in self.graph.nodes() if self.graph.nodes[n].get("type") == "industry"]),
                "ctas": len([n for n in self.graph.nodes() if self.graph.nodes[n].get("type") == "cta"])
            }
        }


if __name__ == "__main__":
    # Create and test the knowledge graph
    kg = MarketingKnowledgeGraph()
    
    # Print summary
    print("Knowledge Graph Summary:")
    print(json.dumps(kg.get_graph_summary(), indent=2))
    
    # Test platform info
    print("\n\nFacebook Platform Info:")
    print(json.dumps(kg.get_platform_info("Facebook"), indent=2))
    
    # Test finding best platforms
    print("\n\nBest platforms for E-commerce Promotional ads:")
    platforms = kg.find_best_platforms(industry="Ecommerce", ad_type="Promotional")
    print(json.dumps(platforms, indent=2))
    
    # Save the graph
    kg.save()