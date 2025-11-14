"""
API routes for user feedback.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from core.database.client import get_supabase_client
from core.database.models import FeedbackRequest, FeedbackResponse
from core.database.repositories.feedback_repository import FeedbackRepository
from ..middleware.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["feedback"])


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    request: FeedbackRequest,
    user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Submit user feedback on tests or recommendations.
    """
    try:
        user_id = user["user_id"]
        
        # Create feedback record
        feedback_repo = FeedbackRepository(supabase)
        feedback_data = {
            "user_id": user_id,
            "test_id": str(request.test_id) if request.test_id else None,
            "recommendation_id": str(request.recommendation_id) if request.recommendation_id else None,
            "rating": request.rating,
            "comment": request.comment
        }
        
        feedback_id = feedback_repo.create_feedback(feedback_data)
        
        logger.info(f"Feedback {feedback_id} submitted by user {user_id}")
        
        return FeedbackResponse(
            feedback_id=feedback_id,
            success=True,
            message="Feedback submitted successfully"
        )
        
    except Exception as e:
        logger.error(f"Failed to submit feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit feedback: {str(e)}"
        )
