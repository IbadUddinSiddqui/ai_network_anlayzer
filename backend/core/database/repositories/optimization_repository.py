"""
Optimization repository for tracking applied optimizations.
"""
import logging
from typing import List, Dict
from supabase import Client

logger = logging.getLogger(__name__)


class OptimizationRepository:
    """
    Repository for optimization history CRUD operations.
    """
    
    def __init__(self, supabase_client: Client):
        self.client = supabase_client
        self.table_name = "optimization_history"
    
    def create_optimization(self, optimization_data: Dict) -> str:
        """
        Create a new optimization record.
        
        Args:
            optimization_data: Optimization data
            
        Returns:
            Created optimization ID
        """
        try:
            response = self.client.table(self.table_name).insert(optimization_data).execute()
            
            if response.data and len(response.data) > 0:
                opt_id = response.data[0]["id"]
                logger.info(f"Optimization {opt_id} created")
                return opt_id
            
            raise Exception("Failed to create optimization")
            
        except Exception as e:
            logger.error(f"Failed to create optimization: {e}")
            raise
    
    def get_user_optimizations(self, user_id: str, limit: int = 20) -> List[Dict]:
        """
        Retrieve user's optimization history.
        
        Args:
            user_id: User UUID
            limit: Maximum number of results
            
        Returns:
            List of optimization dicts
        """
        try:
            response = self.client.table(self.table_name).select("*").eq("user_id", user_id).order("applied_at", desc=True).limit(limit).execute()
            
            logger.info(f"Retrieved {len(response.data)} optimizations for user {user_id}")
            return response.data
            
        except Exception as e:
            logger.error(f"Failed to retrieve optimizations for user {user_id}: {e}")
            raise
