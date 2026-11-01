# MyAdvisor — User Acceptance Testing (UAT) Report

**Student Name:** Daniel Goodridge  
**Student ID:** 816036457 
**Project:** MyAdvisor  
**Testing Date:** 1 November 2026  
**Testing Environment:** Local development environment (`http://127.0.0.1:8000`)

## 1. Introduction

User Acceptance Testing (UAT) was conducted to verify that the MyAdvisor application supports its main user workflows and meets the expected functional requirements.

Testing was performed manually using the application through a web browser.

## 2. UAT Test Results

| Test ID | Test Scenario | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| UAT-01 | Student logs in and opens dashboard | Student dashboard loads successfully | Dashboard loaded successfully | Pass |
| UAT-02 | View degree progress | Degree progress information is displayed | Degree progress displayed | Pass |
| UAT-03 | Create a semester course plan | Student can create a course plan | Course plan created | Pass |
| UAT-04 | Submit a course plan | Plan status changes to Submitted | Status changed to Submitted | Pass |
| UAT-05 | Admin views submitted plan | Submitted plan appears in admin dashboard | Plan appeared in admin dashboard | Pass |
| UAT-06 | Admin approves a plan | Plan status changes to Approved | Plan was approved | Pass |
| UAT-07 | Student views approved plan | Student can see the approved status | Approved status displayed | Pass |
| UAT-08 | Admin rejects another plan | Plan status changes to Rejected | Plan was rejected | Pass |
| UAT-09 | Student revises and resubmits rejected plan | Same plan can be revised and resubmitted | Same plan ID was retained and resubmitted | Pass |
| UAT-10 | Student attempts to access admin dashboard | Unauthorized student access is blocked | Unauthorized page was displayed | Pass |

## 3. Test Summary

- **Total test cases:** 10
- **Passed:** 10
- **Failed:** 0
- **Pass rate:** 100%

## 4. Conclusion

All ten UAT test scenarios were completed successfully.

The testing confirmed that students can view their degree progress, create and submit semester course plans, and view decisions made by administrators. Administrators can review, approve, and reject submitted plans. Students can also revise and resubmit rejected plans while retaining the original plan ID.

The application also prevents student accounts from accessing the administrator dashboard.

Based on the completed UAT scenarios, the tested MyAdvisor workflows satisfied their expected results.