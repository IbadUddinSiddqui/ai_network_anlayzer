# Implementation Plan

- [ ] 1. Update backend response models and data structures
  - Add `data_availability` field to track which test data is present
  - Add `ai_status` field to track AI recommendation generation status separately from test status
  - Create helper function to calculate data availability from test results
  - _Requirements: 1.1, 1.4, 4.4_

- [ ] 2. Decouple AI recommendation generation from test completion
  - [x] 2.1 Modify `execute_network_test()` to store test results immediately when tests complete



    - Update test record with results and status="completed" as soon as tests finish
    - Set `data_availability` based on which tests returned data
    - Set `ai_status` to "pending" initially
    - _Requirements: 1.1, 1.2, 4.2_

  - [ ] 2.2 Move AI analysis to separate try-catch block after test results are stored
    - Wrap AI analysis in its own error handling
    - Update `ai_status` to "completed" when AI succeeds
    - Update `ai_status` to "failed" if AI fails
    - _Requirements: 1.2, 3.2, 5.4_

  - [ ] 2.3 Implement fallback recommendation generation
    - Create `generate_fallback_recommendations()` function with threshold-based logic
    - Generate recommendations for low speed, high latency, packet loss
    - Use fallback recommendations when AI analysis fails
    - _Requirements: 3.2, 5.4_


- [ ] 3. Update frontend polling logic to check for data presence
  - [ ] 3.1 Create `check_results_ready()` helper function
    - Check for presence of any test data (ping, speed, dns, etc.)
    - Return tuple: (ready, has_data, has_ai)
    - Consider results ready if has_data is True, regardless of AI status

    - _Requirements: 1.1, 2.3, 2.4_

  - [ ] 3.2 Modify polling loop to use new data checking logic
    - Replace status-based checking with data presence checking
    - Continue polling until `has_data == True` OR timeout

    - Display results immediately when data is available
    - _Requirements: 2.1, 2.2, 2.3_

  - [ ] 3.3 Improve timeout handling
    - After timeout, check one final time for any available data
    - Display partial results if any data exists
    - Show clear message about what's missing


    - Provide manual refresh option
    - _Requirements: 2.5, 4.3, 4.5_

- [x] 4. Separate AI recommendations display from test results


  - [ ] 4.1 Create separate display section for AI recommendations
    - Show test metrics immediately when available
    - Display AI recommendations section separately below test results
    - Show "AI Analysis Pending" placeholder when recommendations aren't ready
    - _Requirements: 1.2, 3.1, 4.5_

  - [ ] 4.2 Add "Refresh AI Recommendations" button
    - Create button that fetches latest results without re-running tests
    - Update only the AI recommendations section
    - Show loading indicator during refresh
    - _Requirements: 3.3, 3.4_

  - [ ] 4.3 Display fallback recommendations when AI fails
    - Check `ai_status` field in response
    - Show fallback recommendations with appropriate messaging
    - Indicate that these are basic recommendations
    - _Requirements: 3.2_

- [ ] 5. Enhance status communication and error messages
  - [ ] 5.1 Add individual test status badges
    - Display success/failed/skipped status for each test type
    - Use color coding (green/red/gray)
    - Show icons for visual clarity
    - _Requirements: 4.4, 5.5_

  - [ ] 5.2 Improve progress messages during test execution
    - Show specific messages for each test phase
    - Indicate when waiting for AI analysis


    - Display clear completion messages
    - _Requirements: 4.1, 4.2, 4.5_

- [x] 6. Add persistent loader that runs until all tests and results are complete

  - [ ] 6.1 Create continuous loader component
    - Display animated loader/spinner during entire test execution
    - Show progress messages that update based on test phase
    - Keep loader visible until ALL tests complete AND results are fetched
    - _Requirements: 4.1, 4.5_


  - [ ] 6.2 Update loader messages dynamically
    - "Running ping tests..." when ping is executing
    - "Running speed test..." when speed test is executing
    - "Analyzing results with AI..." when AI is processing
    - "Finalizing results..." when wrapping up
    - _Requirements: 4.1, 4.2_

  - [ ] 6.3 Only hide loader when results are fully displayed
    - Keep loader visible during polling
    - Hide loader only after results are rendered on screen
    - Show completion animation before hiding loader
    - _Requirements: 1.1, 4.2_

  - [ ] 5.3 Add detailed error logging
    - Log polling errors with context (test_id, attempt number)
    - Log data availability status on each poll
    - Log AI recommendation status
    - Log timeout events with current state
    - _Requirements: 5.1, 5.2, 5.3, 5.5_

- [ ] 7. Update API response building in get_results endpoint
  - Calculate and include `data_availability` in response
  - Include `ai_status` field in response
  - Add user-friendly `message` field based on current state
  - Handle cases where AI recommendations are missing gracefully
  - _Requirements: 1.4, 3.1, 4.3_

- [ ] 8. Add comprehensive error handling
  - [ ] 8.1 Handle database query failures in backend
    - Add try-catch around database operations
    - Log query details and errors
    - Return appropriate error responses
    - _Requirements: 5.2, 5.3_

  - [ ] 8.2 Handle API errors in frontend polling
    - Distinguish between fatal errors (404, 403) and transient errors
    - Continue polling for transient errors
    - Stop polling and show error for fatal errors
    - _Requirements: 5.1, 5.2_

  - [ ] 8.3 Handle partial test results
    - Display available test data even if some tests failed
    - Show which tests succeeded and which failed
    - Provide error details for failed tests
    - _Requirements: 4.4, 5.5_

- [ ]* 9. Add integration tests for new functionality
  - Test polling with delayed AI recommendations
  - Test display with missing AI recommendations
  - Test timeout behavior with partial results
  - Test manual refresh functionality
  - Test error scenarios (AI failure, database errors)
  - _Requirements: All_
