"""
API routes for network tests.
"""
import logging
import asyncio
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import Dict
from uuid import uuid4

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from core.network.test_runner import NetworkTestRunner
from core.ai import AIAnalyzer
from core.database.client import get_supabase_client
from core.database.models import TestConfig, TestInitiatedResponse, TestResultsResponse
from core.database.repositories.test_repository import TestRepository
from core.database.repositories.recommendation_repository import RecommendationRepository
from ..middleware.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["tests"])


@router.post("/run-test", response_model=TestInitiatedResponse)
async def run_test(
    config: TestConfig,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Initiate a network test.
    
    Starts network tests in background and returns test ID immediately.
    """
    try:
        user_id = user["user_id"]
        test_id = str(uuid4())
        
        logger.info(f"Initiating network test {test_id} for user {user_id}")
        
        # Create test repository
        test_repo = TestRepository(supabase)
        
        # Create initial test record with "running" status
        initial_data = {
            "ping_results": [],
            "jitter_results": {},
            "packet_loss_results": {},
            "speed_results": {},
            "dns_results": [],
            "status": "running"
        }
        
        created_test_id = test_repo.create_test(user_id, initial_data)
        
        # Run tests in background
        background_tasks.add_task(
            execute_network_test,
            created_test_id,
            user_id,
            config,
            supabase
        )
        
        return TestInitiatedResponse(
            test_id=created_test_id,
            status="running",
            message="Network test initiated successfully"
        )
        
    except Exception as e:
        logger.error(f"Failed to initiate test: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate test: {str(e)}"
        )


@router.get("/get-results/{test_id}", response_model=TestResultsResponse)
async def get_results(
    test_id: str,
    user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Retrieve test results and AI recommendations.
    """
    try:
        user_id = user["user_id"]
        
        # Get test
        test_repo = TestRepository(supabase)
        test = test_repo.get_test_by_id(test_id)
        
        if not test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test not found"
            )
        
        # Verify ownership
        if test["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Get recommendations
        rec_repo = RecommendationRepository(supabase)
        recommendations = rec_repo.get_recommendations_by_test_id(test_id)
        
        # Build response
        from core.database.models import NetworkTestResult, AIRecommendation, TestStatus
        from core.database.models import JitterResult, PacketLossResult, SpeedResult
        from core.database.models import TestStatusDetail, TestErrors
        
        # Handle empty results for running tests with proper error logging
        jitter = None
        if test["jitter_results"] and isinstance(test["jitter_results"], dict) and test["jitter_results"]:
            try:
                jitter = JitterResult(**test["jitter_results"])
            except Exception as e:
                logger.error(
                    f"Failed to parse jitter results for test {test_id}: {e}",
                    exc_info=True,
                    extra={"test_id": test_id, "jitter_data": test["jitter_results"]}
                )
                jitter = None
        
        packet_loss = None
        if test["packet_loss_results"] and isinstance(test["packet_loss_results"], dict) and test["packet_loss_results"]:
            try:
                packet_loss = PacketLossResult(**test["packet_loss_results"])
            except Exception as e:
                logger.error(
                    f"Failed to parse packet_loss results for test {test_id}: {e}",
                    exc_info=True,
                    extra={"test_id": test_id, "packet_loss_data": test["packet_loss_results"]}
                )
                packet_loss = None
        
        speed = None
        if test["speed_results"] and isinstance(test["speed_results"], dict) and test["speed_results"]:
            try:
                speed = SpeedResult(**test["speed_results"])
            except Exception as e:
                logger.error(
                    f"Failed to parse speed results for test {test_id}: {e}",
                    exc_info=True,
                    extra={"test_id": test_id, "speed_data": test["speed_results"]}
                )
                speed = None
        
        # Parse test_status and errors if available
        test_status_detail = None
        if test.get("test_status"):
            try:
                test_status_detail = TestStatusDetail(**test["test_status"])
            except Exception as e:
                logger.warning(f"Failed to parse test_status for test {test_id}: {e}")
        
        test_errors = None
        if test.get("errors"):
            try:
                test_errors = TestErrors(**test["errors"])
            except Exception as e:
                logger.warning(f"Failed to parse errors for test {test_id}: {e}")
        
        test_result = NetworkTestResult(
            test_id=test["id"],
            timestamp=test["test_timestamp"],
            ping_results=test["ping_results"] if test["ping_results"] else [],
            jitter_results=jitter,
            packet_loss_results=packet_loss,
            speed_results=speed,
            dns_results=test["dns_results"] if test["dns_results"] else [],
            status=TestStatus(test["status"]),
            test_status=test_status_detail,
            errors=test_errors
        )
        
        ai_recs = [
            AIRecommendation(
                id=rec["id"],
                test_id=rec["test_id"],
                agent_type=rec["agent_type"],
                recommendation_text=rec["recommendation_text"],
                confidence_score=float(rec["confidence_score"]),
                severity=rec["severity"],
                created_at=rec["created_at"]
            )
            for rec in recommendations
        ]
        
        return TestResultsResponse(
            test_results=test_result,
            ai_recommendations=ai_recs,
            status=TestStatus(test["status"])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve results: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve results: {str(e)}"
        )


async def execute_network_test(test_id: str, user_id: str, config: TestConfig, supabase):
    """
    Background task to execute network test and AI analysis with validation and retry.
    """
    from core.validation.test_results import TestResultValidator
    from core.utils.error_handling import retry_async, log_and_capture_exception
    
    try:
        logger.info(f"[Test {test_id}] Executing network test for user {user_id}")
        logger.info(f"[Test {test_id}] Config: hosts={config.target_hosts}, dns={config.dns_servers}, "
                   f"tests enabled: ping={config.run_ping}, jitter={config.run_jitter}, "
                   f"packet_loss={config.run_packet_loss}, speed={config.run_speed}, dns={config.run_dns}")
        
        # Run network tests with selected options
        runner = NetworkTestRunner()
        test_results = await runner.run_all_tests(
            target_hosts=config.target_hosts,
            dns_servers=config.dns_servers,
            packet_count=config.packet_count,
            run_ping=config.run_ping,
            run_jitter=config.run_jitter,
            run_packet_loss=config.run_packet_loss,
            run_speed=config.run_speed,
            run_dns=config.run_dns
        )
        
        # Log test completion status
        overall_status = test_results.get('status', 'unknown')
        logger.info(f"[Test {test_id}] Network tests completed. Overall status: {overall_status}")
        
        # Log detailed results summary
        test_status = test_results.get('test_status', {})
        logger.info(f"[Test {test_id}] Individual test status: {test_status}")
        logger.info(f"[Test {test_id}] Results summary: "
                   f"ping={len(test_results.get('ping_results', []))} hosts, "
                   f"jitter={bool(test_results.get('jitter_results'))}, "
                   f"packet_loss={bool(test_results.get('packet_loss_results'))}, "
                   f"speed={bool(test_results.get('speed_results'))}, "
                   f"dns={len(test_results.get('dns_results', []))} servers")
        
        # Log any errors
        errors = test_results.get('errors', {})
        if any(errors.values()):
            logger.warning(f"[Test {test_id}] Test errors: {errors}")
        
        # Validate results
        validator = TestResultValidator()
        validation = validator.validate_all_results(test_results, config)
        
        if not validation['is_complete']:
            logger.warning(f"[Test {test_id}] Validation issues found:")
            if validation['missing_tests']:
                logger.warning(f"[Test {test_id}] Missing tests: {validation['missing_tests']}")
            if validation['partial_tests']:
                logger.warning(f"[Test {test_id}] Partial tests: {validation['partial_tests']}")
            if validation['validation_errors']:
                for error in validation['validation_errors']:
                    logger.warning(f"[Test {test_id}] Validation error: {error}")
        else:
            logger.info(f"[Test {test_id}] All requested tests completed successfully")
        
        # Determine final status based on validation
        if overall_status == "failed":
            final_status = "failed"
        elif validation['is_complete']:
            final_status = "completed"
        elif validation['successful_tests']:
            final_status = "partial"
        else:
            final_status = "failed"
        
        logger.info(f"[Test {test_id}] Final status: {final_status}")
        
        # Store results with detailed status IMMEDIATELY
        test_data = {
            "ping_results": test_results["ping_results"],
            "jitter_results": test_results["jitter_results"],
            "packet_loss_results": test_results["packet_loss_results"],
            "speed_results": test_results["speed_results"],
            "dns_results": test_results["dns_results"],
            "status": final_status,
            "test_status": test_results.get("test_status", {}),
            "errors": test_results.get("errors", {})
        }
        
        # Update test record - use service key to bypass RLS
        from supabase import create_client
        import os
        service_key = os.getenv('SUPABASE_SERVICE_KEY') or os.getenv('SUPABASE_KEY')
        client = create_client(os.getenv('SUPABASE_URL'), service_key)
        
        logger.info(f"[Test {test_id}] ========== STORING TEST RESULTS IMMEDIATELY ==========")
        logger.info(f"[Test {test_id}] Updating database with test results (before AI analysis)")
        
        # Retry database update
        async def update_database():
            response = client.table("network_tests").update(test_data).eq("id", test_id).execute()
            return response
        
        try:
            response = await retry_async(update_database, max_retries=2, delay=1.0)
            logger.info(f"[Test {test_id}] ✅ Test results stored successfully in database")
            logger.info(f"[Test {test_id}] Frontend can now fetch and display results")
        except Exception as e:
            logger.error(f"[Test {test_id}] ❌ Failed to update database after retries: {e}", exc_info=True)
            raise
        
        # Run AI analysis SEPARATELY (after results are stored)
        logger.info(f"[Test {test_id}] ========== STARTING AI ANALYSIS (ASYNC) ==========")
        analyzer = AIAnalyzer()
        
        try:
            # Retry AI analysis
            logger.info(f"[Test {test_id}] Calling AI analyzer with retry logic...")
            analysis = await retry_async(
                analyzer.analyze,
                test_results,
                max_retries=2,
                delay=1.0
            )
            logger.info(f"[Test {test_id}] ✅ AI analysis completed successfully")
            logger.info(f"[Test {test_id}] Analysis contains {len(analysis.get('recommendations', []))} recommendations")
        except Exception as e:
            logger.error(f"[Test {test_id}] ❌ AI analysis failed after retries: {e}", exc_info=True)
            # Use fallback recommendations
            logger.warning(f"[Test {test_id}] Using fallback recommendations")
            analysis = analyzer._generate_fallback_analysis(test_results)
            logger.info(f"[Test {test_id}] Fallback generated {len(analysis.get('recommendations', []))} recommendations")
        
        # Store recommendations with validation
        rec_repo = RecommendationRepository(supabase)
        recommendations = []
        
        for i, rec in enumerate(analysis.get("recommendations", [])):
            try:
                # Handle both 'text' and 'recommendation_text' keys
                rec_text = rec.get("text") or rec.get("recommendation_text") or rec.get("recommendation", "No recommendation provided")
                
                # Validate required fields
                if not rec_text or len(rec_text.strip()) == 0:
                    logger.warning(f"[Test {test_id}] Skipping recommendation {i}: empty text")
                    continue
                
                rec_data = {
                    "test_id": test_id,
                    "agent_type": rec.get("agent_type") or rec.get("agent_source", "ai_analyzer"),
                    "recommendation_text": rec_text,
                    "confidence_score": float(rec.get("confidence") or rec.get("confidence_score", 0.7)),
                    "severity": rec.get("severity", "info")
                }
                recommendations.append(rec_data)
            except Exception as e:
                logger.warning(f"[Test {test_id}] Failed to process recommendation {i}: {e}")
                continue
        
        # Ensure at least one recommendation
        if not recommendations:
            logger.warning(f"[Test {test_id}] No valid recommendations, adding generic one")
            recommendations.append({
                "test_id": test_id,
                "agent_type": "system",
                "recommendation_text": "Network test completed. Review the results for detailed metrics.",
                "confidence_score": 1.0,
                "severity": "info"
            })
        
        # Store recommendations
        logger.info(f"[Test {test_id}] ========== STORING RECOMMENDATIONS ==========")
        logger.info(f"[Test {test_id}] Attempting to store {len(recommendations)} recommendations")
        try:
            if recommendations:
                rec_repo.bulk_create(recommendations)
                logger.info(f"[Test {test_id}] ✅ Successfully stored {len(recommendations)} recommendations to database")
                
                # Verify they were stored
                stored_recs = rec_repo.get_recommendations_by_test_id(test_id)
                logger.info(f"[Test {test_id}] ✅ Verification: {len(stored_recs)} recommendations found in database")
            else:
                logger.error(f"[Test {test_id}] ❌ No recommendations to store! This should never happen!")
        except Exception as e:
            logger.error(f"[Test {test_id}] ❌ Failed to store recommendations: {e}", exc_info=True)
        
        logger.info(f"[Test {test_id}] ========== TEST EXECUTION COMPLETE ==========")
        logger.info(f"[Test {test_id}] Final Status: {final_status}")
        logger.info(f"[Test {test_id}] Test Results: Stored")
        logger.info(f"[Test {test_id}] AI Recommendations: {len(recommendations)} stored")
        logger.info(f"[Test {test_id}] ================================================")
        
    except Exception as e:
        error_dict = log_and_capture_exception(logger, "execute_network_test", e, test_id)
        logger.error(f"[Test {test_id}] Test execution failed: {e}", exc_info=True)
        
        # Update status to failed with error details
        try:
            from supabase import create_client
            import os
            service_key = os.getenv('SUPABASE_SERVICE_KEY') or os.getenv('SUPABASE_KEY')
            client = create_client(os.getenv('SUPABASE_URL'), service_key)
            
            error_data = {
                "status": "failed",
                "errors": {
                    "system": str(e)
                }
            }
            client.table("network_tests").update(error_data).eq("id", test_id).execute()
            logger.info(f"[Test {test_id}] Updated test status to failed")
        except Exception as update_error:
            logger.error(f"[Test {test_id}] Failed to update test status: {update_error}")
