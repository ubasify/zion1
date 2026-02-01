# Comprehensive Test Case Document: ZynChurch Platform

This document provides a full suite of test cases to verify the recent end-to-end enhancements, including authentication flows, role-level access, new functional modules (Impact/Announcements), and the restructured executive dashboard.

---

## 1. Authentication & Registration
| ID | Test Case | Action | Expected Result |
| :--- | :--- | :--- | :--- |
| 1.1 | **User Registration** | Navigate to `/auth/register`, fill details, select a role | Redirect to login with success message; User record created in DB. |
| 1.2 | **Logout Security** | Click "Log Out" in the sidebar | Session terminated via POST; Redirected to login page. |
| 1.3 | **Session Persistence** | Click "Back" after logout | User redirected to login or denied access; Cannot view private pages. |

## 2. Global Navigation (Sidebar)
| ID | Test Case | Action | Expected Result |
| :--- | :--- | :--- | :--- |
| 2.1 | **Module Visibility** | Log in as Super Admin | All 8 core modules visible: Attendance, Members, Outreach, Impact, Ministries, Portal, Events, Announcements. |
| 2.2 | **Outreach Rebrand** | Check sidebar for "Visitors" | Label is now "Outreach" with a `compass` icon. |
| 2.3 | **Access Restriction** | Log in as Standard User | **Admin Panel** and **Audit Logs** sections are hidden from the sidebar. |

## 3. Executive Dashboard Integration
| ID | Test Case | Action | Expected Result |
| :--- | :--- | :--- | :--- |
| 3.1 | **KPI Grid Layout** | View the main Dashboard | KPI cards are organized in a clean **2x3 grid** layout (3 columns on desktop). |
| 3.2 | **Impact Card** | Check the new **Community Impact** card | Shows current/aggregated count of "People Reached" from DB. |
| 3.3 | **Activity Stream** | View "Recent Activity" list | Includes **Impact Outreach** events alongside Finance/Attendance logs. |
| 3.4 | **Filter Persistence** | Apply a date filter | Dashboard metrics (Attendance, Giving, Impact) update according to the selected range. |

## 4. Community Impact Module
| ID | Test Case | Action | Expected Result |
| :--- | :--- | :--- | :--- |
| 4.1 | **Impact List View** | Navigate to **Community Impact** | Modern list of outreach activities loads with reach metrics. |
| 4.2 | **Record Activity** | Click "Record Impact", fill modal, submit | New record appears in the list and updates the Dashboard total. |

## 5. Announcements Module
| ID | Test Case | Action | Expected Result |
| :--- | :--- | :--- | :--- |
| 5.1 | **Management Hub** | Navigate to **Announcements** | Table of recent announcements loads with visibility status (Public/Member). |
| 5.2 | **Create Announcement**| Click "New", set title/content, toggle "Public" | Announcement is saved and tagged correctly for the Member Portal. |

## 6. Audit & System Administration
| ID | Test Case | Action | Expected Result |
| :--- | :--- | :--- | :--- |
| 6.1 | **Login Tracking** | Log in from a different browser | New entry appears in **System > Audit Logs** with browser/device info. |
| 6.2 | **Log Filtering** | Filter Audit Logs by User or Date | Result set narrows down correctly based on selected parameters. |

---

> [!IMPORTANT]
> **Environment**: All tests should be performed on the staging/production Azure environment after the GitHub Actions deployment is complete.
> **Requirement**: Ensure `startup.sh` has successfully run migrations to support the new `CommunityImpact` and `Announcement` models.
