"""
Supabase client initialization and connection management.
"""
import os
from typing import Optional
from supabase import create_client, Client
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class SupabaseClient:
    """
    Singleton Supabase client for database operations.
    
    Provides connection pooling and error handling for Supabase interactions.
    """
    
    _instance: Optional['SupabaseClient'] = None
    _client: Optional[Client] = None
    
    def __new__(cls):
        """Ensure only one instance of SupabaseClient exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize Supabase client if not already initialized."""
        if self._client is None:
            self._initialize_client()
    
    def _initialize_client(self):
        """
        Initialize the Supabase client with credentials from environment.
        
        Raises:
            ValueError: If required environment variables are missing
            Exception: If connection to Supabase fails
        """
        supabase_url = os.getenv('SUPABASE_URL')
        # Use service_role key for backend to bypass RLS
        supabase_key = os.getenv('SUPABASE_SERVICE_KEY') or os.getenv('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_KEY must be set in environment variables"
            )
        
        try:
            self._client = create_client(supabase_url, supabase_key)
            logger.info("Supabase client initialized successfully with service role")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            raise
    
    @property
    def client(self) -> Client:
        """
        Get the Supabase client instance.
        
        Returns:
            Client: Supabase client for database operations
            
        Raises:
            RuntimeError: If client is not initialized
        """
        if self._client is None:
            raise RuntimeError("Supabase client not initialized")
        return self._client
    
    def health_check(self) -> bool:
        """
        Check if the database connection is healthy.
        
        Returns:
            bool: True if connection is healthy, False otherwise
        """
        try:
            # Simple query to check connection
            response = self.client.table('users').select('id').limit(1).execute()
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    def close(self):
        """Close the Supabase client connection."""
        # Supabase client doesn't require explicit closing
        # but we can reset the instance for testing purposes
        self._client = None
        logger.info("Supabase client connection closed")


def get_supabase_client() -> Client:
    """
    Dependency injection function for FastAPI.
    
    Returns:
        Client: Supabase client instance
        
    Example:
        @app.get("/users")
        async def get_users(client: Client = Depends(get_supabase_client)):
            return client.table('users').select('*').execute()
    """
    return SupabaseClient().client


# Create a global instance for convenience
supabase_client = SupabaseClient()
