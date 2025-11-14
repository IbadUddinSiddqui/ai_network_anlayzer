"""
Feedback repository for user feedback management.
"""
import logging
from typing import List, Dict, Optional
from supabase import Client

logger = logging.getLogger(__name__)


class FeedbackRepository:
    """
    Repository for user feedback CRUD operations.
    """
    
    def __init__(self, supabase_client: Client):
        self.client = supabase_client
        self.table_name = "feedback"
    
    def create_feedback(self, feedback_data: Dict) -> str:
        """
        Create a new feedback record.
        
        Args:
            feedback_data: Feedback data
            
        Returns:
            Created feedback ID
        """
        try:
            response = self.client.table(self.table_name).insert(feedback_data).execute()
            
            if response.data and len(response.data) > 0:
                feedback_id = response.data[0]["id"]
                logger.info(f"Feedback {feedback_id} created")
                return feedback_id
            
            raise Exception("Failed to create feedback")
            
        except Exception as e:
            logger.error(f"Failed to create feedback: {e}")
            raise
    
    def get_user_feedback(self, user_id: str, limit: int = 20) -> List[Dict]:
        """
        Retrieve user's feedback history.
        
        Args:
            user_id: User UUID
            limit: Maximum number of results
            
        Returns:
            List of feedback dicts
        """
        try:
            response = self.client.table(self.table_name).select("*").eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute()
            
            logger.info(f"Retrieved {len(response.data)} feedback entries for user {user_id}")
            return response.data
            
        except Exception as e:
            logger.error(f"Failed to retrieve feedback for user {user_id}: {e}")
            raise
    
    def get_feedback_stats(self) -> Dict:
        """
        Get aggregate feedback statistics.
        
        Returns:
            Dict with feedback stats
        """
        try:
            response = self.client.table(self.table_name).select("rating").execute()
            
            if not response.data:
                return {"total": 0, "average_rating": 0}
            
            ratings = [f["rating"] for f in response.data if f.get("rating")]
            
            return {
                "total": len(ratings),
                "average_rating": sum(ratings) / len(ratings) if ratings else 0,
                "rating_distribution": {
                    "5_star": sum(1 for r in ratings if r == 5),
                    "4_star": sum(1 for r in ratings if r == 4),
                    "3_star": sum(1 for r in ratings if r == 3),
                    "2_star": sum(1 for r in ratings if r == 2),
                    "1_star": sum(1 for r in ratings if r == 1)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get feedback stats: {e}")
            return {"total": 0, "average_rating": 0}
