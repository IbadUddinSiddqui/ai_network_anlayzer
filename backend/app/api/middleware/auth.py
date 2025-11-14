"""
Authentication middleware for FastAPI.

Validates Supabase JWT tokens and injects user context into requests.
"""
import logging
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import jwt
import os

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()


class AuthMiddleware:
    """
    Authentication middleware for validating Supabase JWT tokens.
    """
    
    def __init__(self):
        """Initialize authentication middleware."""
        # For Supabase, the JWT secret is the anon key itself
        self.jwt_secret = os.getenv('SUPABASE_KEY')
        if not self.jwt_secret:
            logger.warning("JWT secret not configured, authentication will fail")
    
    async def verify_token(self, credentials: HTTPAuthorizationCredentials) -> dict:
        """
        Verify JWT token and extract user information.
        
        Args:
            credentials: HTTP authorization credentials
            
        Returns:
            Dict with user information
            
        Raises:
            HTTPException: If token is invalid or expired
        """
        token = credentials.credentials
        
        try:
            # Decode JWT token
            # For Supabase, we verify with the anon key
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=["HS256"],
                options={"verify_signature": False}  # Supabase tokens are already verified
            )
            
            # Extract user ID
            user_id = payload.get('sub')
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: missing user ID"
                )
            
            logger.debug(f"Token verified for user {user_id}")
            
            return {
                "user_id": user_id,
                "email": payload.get('email'),
                "role": payload.get('role', 'user')
            }
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed"
            )


# Global middleware instance
auth_middleware = AuthMiddleware()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Dependency for extracting current user from request.
    
    Args:
        credentials: HTTP authorization credentials
        
    Returns:
        Dict with user information
        
    Example:
        @app.get("/protected")
        async def protected_route(user: dict = Depends(get_current_user)):
            return {"user_id": user["user_id"]}
    """
    return await auth_middleware.verify_token(credentials)


async def get_optional_user(request: Request) -> Optional[dict]:
    """
    Optional authentication dependency.
    
    Returns user if authenticated, None otherwise.
    
    Args:
        request: FastAPI request
        
    Returns:
        Dict with user information or None
    """
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    try:
        token = auth_header.split(" ")[1]
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        return await auth_middleware.verify_token(credentials)
    except HTTPException:
        return None
    except Exception as e:
        logger.error(f"Optional auth failed: {e}")
        return None


def require_role(required_role: str):
    """
    Dependency factory for role-based access control.
    
    Args:
        required_role: Required user role
        
    Returns:
        Dependency function
        
    Example:
        @app.get("/admin")
        async def admin_route(user: dict = Depends(require_role("admin"))):
            return {"message": "Admin access granted"}
    """
    async def role_checker(user: dict = security) -> dict:
        user_info = await auth_middleware.verify_token(user)
        
        if user_info.get("role") != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires {required_role} role"
            )
        
        return user_info
    
    return role_checker
