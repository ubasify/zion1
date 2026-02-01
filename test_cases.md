# Comprehensive Test Case Document: ZynChurch Platform

This document provides a full suite of test cases to verify the end-to-end functionality of the ZynChurch platform, with a specific focus on **CRUD (Create, Read, Update, Delete)** operations across all core modules.

---

## 1. Authentication & System Administration
| ID | Module | Action | Expected Result | Pass (Yes/No) | Remarks |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1.1 | **Auth** | Register a new user at `/auth/register` | User created and redirected to login. | | |
| 1.2 | **Auth** | Log in and then click **Log Out** | Session terminated via POST; redirected to login. | | |
| 1.3 | **Audit** | View **System > Audit Logs** | Logins are captured with IP and Browser details. | | |
| 1.4 | **Access** | Access `/admin-panel/` as a Standard User | **403 Forbidden**; access restricted to Super Admins. | | |

## 2. Member Management (Full CRUD)
| ID | Operation | Action | Expected Result | Pass (Yes/No) | Remarks |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 2.1 | **CREATE** | Navigate to **Members > Create Member** | Member record successfully saved to database. | | |
| 2.2 | **READ** | View the **Member List** and **Profile Detail** | Member info is correctly displayed with full history. | | |
| 2.3 | **UPDATE** | Edit an existing member's phone/address | Changes persist and are visible in the profile. | | |
| 2.4 | **DELETE** | Delete a temporary test member | Record is removed from the list and database. | | |

## 3. Operations & Attendance (Full CRUD)
| ID | Operation | Action | Expected Result | Pass (Yes/No) | Remarks |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 3.1 | **CREATE** | Log a new service at **Attendance > Record** | Total count (Adults + Children) auto-calculates. | | |
| 3.2 | **READ** | View **Attendance List** and filter by date | Correct records are displayed for the period. | | |
| 3.3 | **UPDATE** | Edit counts in a previously logged service | Totals and Dashboard metrics update immediately. | | |
| 3.4 | **DELETE** | Delete an incorrect attendance entry | Entry removed from ledger; Dashboard reflects new data. | | |

## 4. Finance & Budgeting (Full CRUD)
| ID | Operation | Action | Expected Result | Pass (Yes/No) | Remarks |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 4.1 | **CREATE** | Record an Offering in **Finance > Income** | Transaction appears in the General Ledger. | | |
| 4.2 | **READ** | View the **Financial Dashboard** | YTD Income, Expenses, and Net are updated. | | |
| 4.3 | **UPDATE** | Update a Bank Account's current balance | New balance reflected in the Finance summary. | | |
| 4.4 | **DELETE** | (Admin Only) Remove a duplicate expense | Financial totals and reports recalibrate correctly. | | |

## 5. Ministry & Outreach
| ID | Module | Action | Expected Result | Pass (Yes/No) | Remarks |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 5.1 | **Ministry** | **CRUD**: Create, Edit, and List Ministries | Ministry structure correctly managed; shown in Sidebar. | | |
| 5.2 | **Outreach** | Convert a **Visitor** to a **Member** | Visitor status updates to "Converted"; Member record created. | | |
| 5.3 | **Impact** | Record a **Community Impact** event | "People Reached" metric updates on the Main Dashboard. | | |
| 5.4 | **Announce** | Manage **Announcements** (Create/Edit) | Announcements appear in the Member Portal carousel. | | |

## 6. Dashboard & UI Consistency
| ID | Area | Action | Expected Result | Pass (Yes/No) | Remarks |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 6.1 | **Layout** | Review Dashboard **2x3 KPI Grid** | All 6 key metrics (Attendance, Members, etc.) visible. | | |
| 6.2 | **Theme** | Toggle **Dark/Light Mode** | Soft Off-White theme remains consistent in light mode. | | |
| 6.3 | **Activity** | Post a transaction and check Dashboard | **Recent Activity** stream updates in real-time. | | |

---

> [!IMPORTANT]
> **Data Integrity**: When testing DELETE operations, ensure you are only deleting test data.
> **Deployment**: Verify that `startup.sh` has executed migrations so the new model fields for Impact and Announcements are live.
