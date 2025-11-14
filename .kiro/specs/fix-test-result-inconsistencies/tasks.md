# Implementation Plan

- [x] 1. Create error handling and retry utilities


  - Create `backend/core/utils/error_handling.py` with exception classes and retry logic
  - Implement `log_and_capture_exception` function for consistent error logging
  - Implement `retry_async` function with exponential backoff
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 3.1, 3.2, 3.3, 3.4_



- [ ] 2. Create result validation module
  - Create `backend/core/validation/__init__.py`
  - Create `backend/core/validation/test_results.py` with `TestResultValidator` class
  - Implement validation methods for each test type (ping, speed, packet_loss, jitter, dns)


  - Implement `validate_all_results` method to check completeness
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_

- [ ] 3. Update database models for detailed status tracking
  - Add `PARTIAL` status to `TestStatus` enum in `backend/core/database/models.py`
  - Create `IndividualTestStatus` enum (SUCCESS, FAILED, SKIPPED)


  - Create `TestStatusDetail` model to track each test type status
  - Create `TestErrors` model to store error messages
  - Update `NetworkTestResult` model to include `test_status` and `errors` fields
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_



- [ ] 4. Add database migration for new columns
  - Create migration file `database/migrations/add_test_status_columns.sql`
  - Add `test_status` JSONB column to `network_tests` table
  - Add `errors` JSONB column to `network_tests` table
  - Update default values for new columns
  - _Requirements: 8.1, 8.2, 8.3_

- [ ] 5. Enhance NetworkTestRunner with retry logic
  - Add `TestResultValidator` instance to `NetworkTestRunner.__init__`



  - Add `max_retries` and `retry_delay` configuration
  - Create `_run_test_with_retry` method that wraps test execution with retry logic
  - Update `_run_ping_tests` to use retry logic and return status
  - Update `_run_jitter_tests` to use retry logic and return status
  - Update `_run_packet_loss_test` to use retry logic and return status
  - Update `_run_speed_test` to use retry logic and return status


  - Update `_run_dns_tests` to use retry logic and return status
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ] 6. Update NetworkTestRunner to return detailed status
  - Modify `run_all_tests` to track individual test status
  - Add `test_status` dict to results with status for each test type
  - Add `errors` dict to results with error messages for failed tests


  - Validate results after each test completes
  - Determine overall status (completed/partial/failed) based on validation
  - Continue executing remaining tests even if some fail
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 8.1, 8.2, 8.3, 8.4, 8.5_

- [ ] 7. Fix silent exception handling in API routes
  - In `backend/app/api/routes/tests.py`, replace bare `except: pass` with proper logging
  - Update jitter_results parsing to log exceptions with full context
  - Update packet_loss_results parsing to log exceptions with full context
  - Update speed_results parsing to log exceptions with full context

  - Update dns_results parsing to log exceptions with full context
  - Add exception details to response when parsing fails
  - _Requirements: 1.1, 1.2, 4.1, 4.2, 4.3, 4.4, 4.5_

- [ ] 8. Enhance execute_network_test with validation and retry
  - Import `TestResultValidator` and `retry_async` utilities
  - Add result validation after test execution


  - Determine test status based on validation results
  - Include `test_status` and `errors` in database update
  - Add retry logic for AI analysis (2 retries with 1s delay)
  - Use fallback recommendations if AI analysis fails after retries
  - Ensure recommendations are always stored (even if fallback)


  - Add comprehensive error logging throughout
  - Update test status to "failed" with error details on exception
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 2.5, 2.6, 3.5, 4.6, 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ] 9. Add recommendation validation and storage
  - Create helper function `validate_recommendation` to check required fields


  - Update recommendation storage to validate each recommendation
  - Log warnings for invalid recommendations but continue with valid ones
  - Ensure at least one recommendation is stored (use generic if needed)
  - Add error handling for bulk_create failures
  - _Requirements: 6.2, 6.3, 6.4_

- [x] 10. Update frontend to display test status indicators


  - In `frontend/app.py`, add test status display section after results
  - Create status indicator UI with icons (✅ success, ❌ failed, ⏭️ skipped)
  - Display status for each test type (ping, jitter, packet_loss, speed, dns)
  - Show overall test status (completed/partial/failed)
  - _Requirements: 7.1, 7.2, 8.1, 8.2, 8.3, 8.4, 8.5_



- [ ] 11. Add error display to frontend
  - Add expandable "View Test Errors" section in frontend
  - Display error messages for each failed test
  - Show warning when results are partial
  - Add explanation when AI recommendations are missing

  - Provide troubleshooting guidance for common errors
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ] 12. Add health check for test components
  - Create `backend/core/utils/health_check.py` module
  - Add function to check ping3 library availability
  - Add function to check speedtest-cli availability


  - Add function to check Gemini API key configuration
  - Log warnings for missing components at startup
  - Add health check endpoint to API
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ] 13. Improve AI analyzer error handling
  - Update `AIAnalyzer.analyze` to use retry logic from error_handling module
  - Add detailed logging for each retry attempt
  - Improve fallback analysis to be more informative
  - Validate analysis response before returning
  - Handle rate limit errors specifically
  - _Requirements: 1.3, 3.5, 6.1, 6.5_

- [ ] 14. Update test repository for new fields
  - Update `TestRepository.create_test` to initialize test_status and errors fields
  - Update `TestRepository.update_test_status` to handle new status values
  - Add method to update test with error details
  - Ensure backward compatibility with existing tests
  - _Requirements: 1.6, 2.6_

- [ ] 15. Add comprehensive logging throughout
  - Add INFO logs for test start/completion in test_runner
  - Add WARNING logs for validation failures
  - Add ERROR logs for test failures with full context
  - Add DEBUG logs for test progress
  - Ensure all logs include test_id for traceability
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6_

- [ ] 16. Test the complete flow
  - Run tests with all tests enabled and verify success
  - Run tests with network disconnected to verify error handling
  - Run tests without admin privileges to verify permission errors
  - Verify partial results are displayed correctly
  - Verify AI recommendations always appear (fallback if needed)
  - Verify error messages are clear and helpful
  - Check logs for proper error tracking
  - _Requirements: All_
