"""
Evaluation Metrics for the Marketing Agent
"""

import re
import json
from typing import List, Dict
from rouge_score import rouge_scorer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class AgentEvaluator:
    def __init__(self):
        self.rouge_scorer = rouge_scorer.RougeScorer(
            ['rouge1', 'rouge2', 'rougeL'],
            use_stemmer=True
        )
    
    def evaluate_relevance(self, query: str, response: str, 
                          query_embedding, response_embedding) -> float:
        """
        Evaluate relevance using cosine similarity between query and response embeddings
        
        Args:
            query: User query
            response: Agent response
            query_embedding: Embedding vector for query
            response_embedding: Embedding vector for response
        
        Returns:
            Relevance score (0-1)
        """
        similarity = cosine_similarity(
            [query_embedding], 
            [response_embedding]
        )[0][0]
        
        return float(similarity)
    
    def evaluate_rouge(self, generated: str, reference: str) -> Dict[str, float]:
        """
        Evaluate text quality using ROUGE scores
        
        Args:
            generated: Generated text
            reference: Reference/gold standard text
        
        Returns:
            Dictionary with ROUGE-1, ROUGE-2, ROUGE-L F1 scores
        """
        scores = self.rouge_scorer.score(reference, generated)
        
        return {
            'rouge1': scores['rouge1'].fmeasure,
            'rouge2': scores['rouge2'].fmeasure,
            'rougeL': scores['rougeL'].fmeasure
        }
    
    def check_platform_compliance(self, copy: str, platform_constraints: dict) -> dict:
        """
        Check if generated copy complies with platform constraints
        
        Args:
            copy: Generated ad copy
            platform_constraints: Dict with char_limit, hashtag_limit, etc.
        
        Returns:
            Compliance report
        """
        char_limit = platform_constraints.get('char_limit', 
                                             platform_constraints.get('headline_limit', 999))
        hashtag_limit = platform_constraints.get('hashtag_limit', 999)
        
        copy_length = len(copy)
        hashtag_count = len(re.findall(r'#\w+', copy))
        
        compliant = (copy_length <= char_limit) and (hashtag_count <= hashtag_limit)
        
        return {
            'compliant': compliant,
            'length': copy_length,
            'char_limit': char_limit,
            'within_limit': copy_length <= char_limit,
            'hashtag_count': hashtag_count,
            'hashtag_limit': hashtag_limit,
            'hashtags_within_limit': hashtag_count <= hashtag_limit
        }
    
    def check_hallucination(self, response: str, source_documents: List[str]) -> dict:
        """
        Check for hallucination by verifying if key facts appear in source documents
        
        Args:
            response: Generated response
            source_documents: List of source document texts
        
        Returns:
            Hallucination analysis
        """
        # Extract numbers and specific claims from response
        numbers_in_response = re.findall(r'\d+\.?\d*%?', response)
        
        # Check if numbers appear in source documents
        source_text = ' '.join(source_documents)
        
        verified_numbers = 0
        for number in numbers_in_response:
            if number in source_text:
                verified_numbers += 1
        
        total_numbers = len(numbers_in_response)
        
        if total_numbers == 0:
            hallucination_rate = 0.0
            confidence = "high"
        else:
            hallucination_rate = 1 - (verified_numbers / total_numbers)
            
            if hallucination_rate < 0.2:
                confidence = "high"
            elif hallucination_rate < 0.5:
                confidence = "medium"
            else:
                confidence = "low"
        
        return {
            'hallucination_rate': round(hallucination_rate, 3),
            'total_claims': total_numbers,
            'verified_claims': verified_numbers,
            'confidence': confidence
        }
    
    def evaluate_tone_match(self, copy: str, target_tone: str) -> dict:
        """
        Evaluate if the generated copy matches the target tone
        Uses keyword matching (can be improved with sentiment analysis)
        
        Args:
            copy: Generated ad copy
            target_tone: Target tone (e.g., "professional", "casual", "urgent")
        
        Returns:
            Tone match analysis
        """
        tone_keywords = {
            'professional': ['solution', 'expertise', 'optimize', 'streamline', 'efficient', 
                           'innovative', 'industry', 'proven', 'reliable'],
            'casual': ['hey', 'awesome', 'cool', 'check out', 'super', 'yeah', 
                      'totally', 'fun', 'love'],
            'urgent': ['now', 'today', 'limited', 'hurry', 'don\'t miss', 'act fast',
                      'ends soon', 'last chance', 'immediately'],
            'playful': ['fun', 'exciting', 'yay', 'wow', 'amazing', 'fantastic',
                       '!', 'adventure', 'magical'],
            'informative': ['learn', 'discover', 'understand', 'guide', 'tips',
                          'how to', 'facts', 'information', 'research'],
            'friendly': ['we', 'you', 'together', 'help', 'support', 'welcome',
                        'community', 'happy', 'thanks']
        }
        
        copy_lower = copy.lower()
        target_keywords = tone_keywords.get(target_tone.lower(), [])
        
        matches = sum(1 for keyword in target_keywords if keyword in copy_lower)
        
        match_percentage = (matches / len(target_keywords)) if target_keywords else 0
        
        return {
            'target_tone': target_tone,
            'matched_keywords': matches,
            'total_keywords': len(target_keywords),
            'match_score': round(match_percentage, 3),
            'assessment': 'good' if match_percentage > 0.3 else 'needs_improvement'
        }
    
    def evaluate_cta_presence(self, copy: str) -> dict:
        """
        Check if copy contains a call-to-action
        
        Args:
            copy: Generated ad copy
        
        Returns:
            CTA analysis
        """
        cta_patterns = [
            r'shop now', r'buy now', r'learn more', r'sign up', r'get started',
            r'download', r'book now', r'try free', r'contact us', r'join',
            r'discover', r'explore', r'subscribe', r'register', r'claim'
        ]
        
        copy_lower = copy.lower()
        
        found_ctas = []
        for pattern in cta_patterns:
            if re.search(pattern, copy_lower):
                found_ctas.append(pattern)
        
        return {
            'has_cta': len(found_ctas) > 0,
            'cta_count': len(found_ctas),
            'found_ctas': found_ctas,
            'assessment': 'present' if found_ctas else 'missing'
        }
    
    def comprehensive_evaluation(self, 
                                query: str,
                                generated_copy: str,
                                platform: str,
                                platform_constraints: dict,
                                target_tone: str,
                                source_documents: List[str] = None,
                                reference_copy: str = None) -> dict:
        """
        Perform comprehensive evaluation of generated ad copy
        
        Args:
            query: Original query
            generated_copy: Generated ad copy
            platform: Target platform
            platform_constraints: Platform constraints
            target_tone: Target tone
            source_documents: Source documents for hallucination check
            reference_copy: Reference copy for ROUGE scores
        
        Returns:
            Complete evaluation report
        """
        results = {
            'query': query,
            'generated_copy': generated_copy,
            'platform': platform,
            'evaluations': {}
        }
        
        # 1. Platform Compliance
        results['evaluations']['compliance'] = self.check_platform_compliance(
            generated_copy, 
            platform_constraints
        )
        
        # 2. Tone Match
        results['evaluations']['tone_match'] = self.evaluate_tone_match(
            generated_copy,
            target_tone
        )
        
        # 3. CTA Presence
        results['evaluations']['cta'] = self.evaluate_cta_presence(generated_copy)
        
        # 4. Hallucination Check (if source documents provided)
        if source_documents:
            results['evaluations']['hallucination'] = self.check_hallucination(
                generated_copy,
                source_documents
            )
        
        # 5. ROUGE Scores (if reference provided)
        if reference_copy:
            results['evaluations']['rouge'] = self.evaluate_rouge(
                generated_copy,
                reference_copy
            )
        
        # 6. Calculate Overall Score
        scores = []
        
        if results['evaluations']['compliance']['compliant']:
            scores.append(1.0)
        else:
            scores.append(0.5)
        
        scores.append(results['evaluations']['tone_match']['match_score'])
        
        if results['evaluations']['cta']['has_cta']:
            scores.append(1.0)
        else:
            scores.append(0.3)
        
        if source_documents and 'hallucination' in results['evaluations']:
            scores.append(1 - results['evaluations']['hallucination']['hallucination_rate'])
        
        overall_score = sum(scores) / len(scores)
        
        results['overall_score'] = round(overall_score, 3)
        results['grade'] = self._score_to_grade(overall_score)
        
        return results
    
    def _score_to_grade(self, score: float) -> str:
        """Convert numerical score to letter grade"""
        if score >= 0.9:
            return 'A'
        elif score >= 0.8:
            return 'B'
        elif score >= 0.7:
            return 'C'
        elif score >= 0.6:
            return 'D'
        else:
            return 'F'
    
    def batch_evaluate(self, test_cases: List[dict]) -> dict:
        """
        Evaluate multiple test cases and aggregate results
        
        Args:
            test_cases: List of test case dictionaries
        
        Returns:
            Aggregated evaluation report
        """
        results = []
        
        for test_case in test_cases:
            result = self.comprehensive_evaluation(**test_case)
            results.append(result)
        
        # Aggregate statistics
        overall_scores = [r['overall_score'] for r in results]
        
        aggregated = {
            'total_tests': len(test_cases),
            'average_score': round(np.mean(overall_scores), 3),
            'median_score': round(np.median(overall_scores), 3),
            'min_score': round(np.min(overall_scores), 3),
            'max_score': round(np.max(overall_scores), 3),
            'grade_distribution': {},
            'individual_results': results
        }
        
        # Grade distribution
        grades = [r['grade'] for r in results]
        for grade in ['A', 'B', 'C', 'D', 'F']:
            aggregated['grade_distribution'][grade] = grades.count(grade)
        
        return aggregated


if __name__ == "__main__":
    # Test the evaluator
    evaluator = AgentEvaluator()
    
    # Example test case
    test_case = {
        'query': 'Create Facebook ad for summer sale',
        'generated_copy': '☀️ Summer Sale! Save 50% on everything. Shop now! Limited time offer.',
        'platform': 'Facebook',
        'platform_constraints': {'char_limit': 125, 'hashtag_limit': 3},
        'target_tone': 'urgent',
        'source_documents': ['Summer sales typically see 50% discounts', 'Shop now is an effective CTA'],
        'reference_copy': 'Big summer sale! Save 50% on all items. Shop today!'
    }
    
    result = evaluator.comprehensive_evaluation(**test_case)
    
    print("=== Evaluation Report ===")
    print(json.dumps(result, indent=2))