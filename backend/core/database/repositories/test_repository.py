"""
Test repository for network test results management.
"""
import logging
from typing import List, Dict, Optional
from uuid import UUID
from supabase import Client

logger = logging.getLogger(__name__)


class TestRepository:
    """
    Repository for network test CRUD operations.
    
    Handles storage and retrieval of network test results with JSONB data.
    """
    
    def __init__(self, supabase_client: Client):
        """
        Initialize test repository.
        
        Args:
            supabase_client: Supabase client instance
        """
        self.client = supabase_client
        self.table_name = "network_tests"
    
    def create_test(self, user_id: str, test_data: Dict) -> str:
        """
        Create a new network test record with enhanced status tracking.
        
        Args:
            user_id: User UUID
            test_data: Test results data
            
        Returns:
            Created test ID
        """
        try:
            test_record = {
                "user_id": user_id,
                "ping_results": test_data.get("ping_results", []),
                "jitter_results": test_data.get("jitter_results", {}),
                "packet_loss_results": test_data.get("packet_loss_results", {}),
                "speed_results": test_data.get("speed_results", {}),
                "dns_results": test_data.get("dns_results", []),
                "status": test_data.get("status", "completed"),
                "test_status": test_data.get("test_status", {}),
                "errors": test_data.get("errors", {})
            }
            
            response = self.client.table(self.table_name).insert(test_record).execute()
            
            if response.data and len(response.data) > 0:
                test_id = response.data[0]["id"]
                logger.info(f"Test {test_id} created for user {user_id}")
                return test_id
            
            raise Exception("Failed to create test: No data returned")
            
        except Exception as e:
            logger.error(f"Failed to create test for user {user_id}: {e}")
            raise
    
    def get_test_by_id(self, test_id: str) -> Optional[Dict]:
        """
        Retrieve test by ID.
        
        Args:
            test_id: Test UUID
            
        Returns:
            Test dict or None if not found
        """
        try:
            response = self.client.table(self.table_name).select("*").eq("id", test_id).execute()
            
            if response.data and len(response.data) > 0:
                logger.info(f"Test {test_id} retrieved successfully")
                return response.data[0]
            
            logger.warning(f"Test {test_id} not found")
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve test {test_id}: {e}")
            raise
    
    def get_user_tests(
        self,
        user_id: str,
        limit: int = 10,
        offset: int = 0,
        status: Optional[str] = None
    ) -> List[Dict]:
        """
        Retrieve user's test history with pagination.
        
        Args:
            user_id: User UUID
            limit: Maximum number of results
            offset: Number of results to skip
            status: Optional status filter
            
        Returns:
            List of test dicts
        """
        try:
            query = self.client.table(self.table_name).select("*").eq("user_id", user_id)
            
            if status:
                query = query.eq("status", status)
            
            query = query.order("test_timestamp", desc=True).range(offset, offset + limit - 1)
            
            response = query.execute()
            
            logger.info(f"Retrieved {len(response.data)} tests for user {user_id}")
            return response.data
            
        except Exception as e:
            logger.error(f"Failed to retrieve tests for user {user_id}: {e}")
            raise
    
    def update_test_status(self, test_id: str, status: str) -> Dict:
        """
        Update test status.
        
        Args:
            test_id: Test UUID
            status: New status (running, completed, partial, failed)
            
        Returns:
            Updated test dict
        """
        try:
            response = self.client.table(self.table_name).update({"status": status}).eq("id", test_id).execute()
            
            if response.data and len(response.data) > 0:
                logger.info(f"Test {test_id} status updated to {status}")
                return response.data[0]
            
            raise Exception(f"Test {test_id} not found")
            
        except Exception as e:
            logger.error(f"Failed to update test {test_id} status: {e}")
            raise
    
    def update_test_with_error(self, test_id: str, error_message: str, test_type: Optional[str] = None) -> Dict:
        """
        Update test with error details.
        
        Args:
            test_id: Test UUID
            error_message: Error message to store
            test_type: Optional specific test type that failed (ping, jitter, etc.)
            
        Returns:
            Updated test dict
        """
        try:
            update_data = {"status": "failed"}
            
            if test_type:
                # Update specific test error
                update_data["errors"] = {test_type: error_message}
            else:
                # Update general error
                update_data["errors"] = {"system": error_message}
            
            response = self.client.table(self.table_name).update(update_data).eq("id", test_id).execute()
            
            if response.data and len(response.data) > 0:
                logger.info(f"Test {test_id} updated with error: {error_message}")
                return response.data[0]
            
            raise Exception(f"Test {test_id} not found")
            
        except Exception as e:
            logger.error(f"Failed to update test {test_id} with error: {e}")
            raise
    
    def delete_test(self, test_id: str) -> bool:
        """
        Delete test record.
        
        Args:
            test_id: Test UUID
            
        Returns:
            True if deleted successfully
        """
        try:
            response = self.client.table(self.table_name).delete().eq("id", test_id).execute()
            logger.info(f"Test {test_id} deleted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete test {test_id}: {e}")
            raise
    
    def get_user_test_count(self, user_id: str) -> int:
        """
        Get total number of tests for a user.
        
        Args:
            user_id: User UUID
            
        Returns:
            Count of tests
        """
        try:
            response = self.client.table(self.table_name).select("id", count="exact").eq("user_id", user_id).execute()
            return response.count if response.count else 0
            
        except Exception as e:
            logger.error(f"Failed to count tests for user {user_id}: {e}")
            return 0
