# MyAdvisor — Unit and Integration Test Plans

**Project:** MyAdvisor  
**Student:** Daniel Goodridge  
**Student ID:** 816036457 
**Date:** 1 November 2026

---

# 1. Unit Test Plan

## 1.1 Purpose

The purpose of unit testing is to verify that individual components of the MyAdvisor application operate correctly in isolation. Testing focuses on the course planning service and degree progress calculations.

## 1.2 Testing Approach

- Testing framework: pytest
- Test location: `tests/test_course_plan_service.py`
- Database: Isolated SQLite test database
- Execution: Command-line testing using pytest

## 1.3 Test Cases

| Test ID | Test Description | Expected Result |
|---|---|---|
| UT-01 | Test course plan submission and administrative decision | Plan can be submitted and subsequently approved or rejected |
| UT-02 | Test admin dashboard plan retrieval | Admin dashboard includes plans assigned to another advisor |
| UT-03 | Test student degree progress calculation | Progress is calculated using course item statuses rather than overall plan approval status |

## 1.4 Expected Outcome

All unit tests should pass without errors. Each test should confirm that its corresponding service or calculation behaves as expected.

---

# 2. Integration Test Plan

## 2.1 Purpose

The purpose of integration testing is to verify that different components of MyAdvisor work together correctly. This includes authentication, database operations, student workflows, administrative functions, and access control.

## 2.2 Testing Approach

- Testing framework: pytest
- HTTP testing: FastAPI TestClient
- Database: Isolated SQLite test database
- Test location: `tests/integration/test_workflows.py`
- Execution: Command-line testing using pytest

## 2.3 Test Cases

| Test ID | Test Description | Expected Result |
|---|---|---|
| IT-01 | Student logs in and opens dashboard | Student dashboard loads successfully |
| IT-02 | Student opens course planning page | Course planning page loads successfully |
| IT-03 | Student creates a course plan | Course plan and associated course items are saved |
| IT-04 | Student attempts to access admin dashboard | Access is denied |
| IT-05 | Admin opens admin dashboard | Admin dashboard loads successfully |
| IT-06 | Unauthenticated visitor attempts to access student dashboard | Access is denied |

## 2.4 Test Data

The integration tests use test student and administrator accounts.

Test data is created in an isolated SQLite database to avoid modifying the application's normal development database.

## 2.5 Expected Outcome

All integration tests should pass. The tests should demonstrate that authentication, authorization, database interactions, and the main student and administrator workflows operate correctly.

---

# 3. Test Execution

The unit and integration test suites are executed using:

```bash
PYTHONPATH=. python3 -m pytest -v
```

## 3.1 Recorded Test Results

| Test Category | Result |
|---|---:|
| Unit tests | 3 passed |
| Integration tests | 6 passed |
| Test setup and health checks | 4 passed |
| Total | 13 passed |
| Failed | 0 |

## 3.2 Conclusion

The unit and integration test suites completed successfully, with all 13 tests passing. The results indicate that the tested application components and their interactions behaved as expected.

