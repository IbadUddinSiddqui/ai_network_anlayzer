"""
User repository for user profile management.
"""
import logging
from typing import Optional, Dict
from uuid import UUID
from supabase import Client

logger = logging.getLogger(__name__)


class UserRepository:
    """
    Repository for user profile CRUD operations.
    
    Handles user data management with Supabase Auth integration.
    """
    
    def __init__(self, supabase_client: Client):
        """
        Initialize user repository.
        
        Args:
            supabase_client: Supabase client instance
        """
        self.client = supabase_client
        self.table_name = "users"
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """
        Retrieve user by ID.
        
        Args:
            user_id: User UUID
            
        Returns:
            User dict or None if not found
        """
        try:
            response = self.client.table(self.table_name).select("*").eq("id", user_id).execute()
            
            if response.data and len(response.data) > 0:
                logger.info(f"User {user_id} retrieved successfully")
                return response.data[0]
            
            logger.warning(f"User {user_id} not found")
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve user {user_id}: {e}")
            raise
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """
        Retrieve user by email.
        
        Args:
            email: User email address
            
        Returns:
            User dict or None if not found
        """
        try:
            response = self.client.table(self.table_name).select("*").eq("email", email).execute()
            
            if response.data and len(response.data) > 0:
                logger.info(f"User with email {email} retrieved successfully")
                return response.data[0]
            
            logger.warning(f"User with email {email} not found")
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve user by email {email}: {e}")
            raise
    
    def create_user(self, user_id: str, email: str) -> Dict:
        """
        Create a new user profile.
        
        Args:
            user_id: User UUID from Supabase Auth
            email: User email address
            
        Returns:
            Created user dict
        """
        try:
            user_data = {
                "id": user_id,
                "email": email
            }
            
            response = self.client.table(self.table_name).insert(user_data).execute()
            
            if response.data and len(response.data) > 0:
                logger.info(f"User {user_id} created successfully")
                return response.data[0]
            
            raise Exception("Failed to create user: No data returned")
            
        except Exception as e:
            logger.error(f"Failed to create user {user_id}: {e}")
            raise
    
    def update_user(self, user_id: str, updates: Dict) -> Dict:
        """
        Update user profile.
        
        Args:
            user_id: User UUID
            updates: Dict of fields to update
            
        Returns:
            Updated user dict
        """
        try:
            response = self.client.table(self.table_name).update(updates).eq("id", user_id).execute()
            
            if response.data and len(response.data) > 0:
                logger.info(f"User {user_id} updated successfully")
                return response.data[0]
            
            raise Exception(f"User {user_id} not found")
            
        except Exception as e:
            logger.error(f"Failed to update user {user_id}: {e}")
            raise
    
    def delete_user(self, user_id: str) -> bool:
        """
        Delete user profile.
        
        Args:
            user_id: User UUID
            
        Returns:
            True if deleted successfully
        """
        try:
            response = self.client.table(self.table_name).delete().eq("id", user_id).execute()
            logger.info(f"User {user_id} deleted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete user {user_id}: {e}")
            raise
