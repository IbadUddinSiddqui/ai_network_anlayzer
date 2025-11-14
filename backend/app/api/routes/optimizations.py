"""
API routes for optimization actions.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from core.database.client import get_supabase_client
from core.database.models import OptimizationActionRequest, OptimizationResponse
from core.database.repositories.optimization_repository import OptimizationRepository
from core.database.repositories.recommendation_repository import RecommendationRepository
from ..middleware.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["optimizations"])


@router.post("/apply-optimization", response_model=OptimizationResponse)
async def apply_optimization(
    request: OptimizationActionRequest,
    user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Record an optimization action taken by the user.
    """
    try:
        user_id = user["user_id"]
        
        # Verify recommendation exists and user owns it
        rec_repo = RecommendationRepository(supabase)
        recommendation = rec_repo.get_recommendation_by_id(str(request.recommendation_id))
        
        if not recommendation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recommendation not found"
            )
        
        # Create optimization record
        opt_repo = OptimizationRepository(supabase)
        opt_data = {
            "user_id": user_id,
            "recommendation_id": str(request.recommendation_id),
            "action_taken": request.action_taken,
            "notes": request.notes
        }
        
        optimization_id = opt_repo.create_optimization(opt_data)
        
        logger.info(f"Optimization {optimization_id} recorded for user {user_id}")
        
        return OptimizationResponse(
            optimization_id=optimization_id,
            success=True,
            message="Optimization recorded successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to record optimization: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record optimization: {str(e)}"
        )
