"""
Recommendation repository for AI recommendations management.
"""
import logging
from typing import List, Dict, Optional
from supabase import Client

logger = logging.getLogger(__name__)


class RecommendationRepository:
    """
    Repository for AI recommendation CRUD operations.
    """
    
    def __init__(self, supabase_client: Client):
        self.client = supabase_client
        self.table_name = "ai_recommendations"
    
    def create_recommendation(self, recommendation_data: Dict) -> str:
        """
        Create a new AI recommendation.
        
        Args:
            recommendation_data: Recommendation data
            
        Returns:
            Created recommendation ID
        """
        try:
            response = self.client.table(self.table_name).insert(recommendation_data).execute()
            
            if response.data and len(response.data) > 0:
                rec_id = response.data[0]["id"]
                logger.info(f"Recommendation {rec_id} created")
                return rec_id
            
            raise Exception("Failed to create recommendation")
            
        except Exception as e:
            logger.error(f"Failed to create recommendation: {e}")
            raise
    
    def bulk_create(self, recommendations: List[Dict]) -> List[str]:
        """
        Create multiple recommendations at once.
        
        Args:
            recommendations: List of recommendation dicts
            
        Returns:
            List of created recommendation IDs
        """
        try:
            response = self.client.table(self.table_name).insert(recommendations).execute()
            
            if response.data:
                rec_ids = [rec["id"] for rec in response.data]
                logger.info(f"Created {len(rec_ids)} recommendations")
                return rec_ids
            
            raise Exception("Failed to create recommendations")
            
        except Exception as e:
            logger.error(f"Failed to bulk create recommendations: {e}")
            raise
    
    def get_recommendations_by_test_id(self, test_id: str) -> List[Dict]:
        """
        Retrieve all recommendations for a test.
        
        Args:
            test_id: Test UUID
            
        Returns:
            List of recommendation dicts
        """
        try:
            response = self.client.table(self.table_name).select("*").eq("test_id", test_id).order("confidence_score", desc=True).execute()
            
            logger.info(f"Retrieved {len(response.data)} recommendations for test {test_id}")
            return response.data
            
        except Exception as e:
            logger.error(f"Failed to retrieve recommendations for test {test_id}: {e}")
            raise
    
    def get_recommendation_by_id(self, recommendation_id: str) -> Optional[Dict]:
        """
        Retrieve recommendation by ID.
        
        Args:
            recommendation_id: Recommendation UUID
            
        Returns:
            Recommendation dict or None
        """
        try:
            response = self.client.table(self.table_name).select("*").eq("id", recommendation_id).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve recommendation {recommendation_id}: {e}")
            raise
