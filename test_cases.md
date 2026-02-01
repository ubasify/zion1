# Test Case Document: ZynChurch Platform Enhancements

This document outlines the test cases required to verify the implementation of the Registration Feature, Admin Access Control, Audit Logs, and UI Refinements.

---

## 1. User Registration Flow
| Step | Action | Expected Result |
| :--- | :--- | :--- |
| 1.1 | Navigate to `/auth/register` | Registration page loads with Glassmorphism styling and "First Timer/Worker/Member" dropdown. |
| 1.2 | Fill in valid details, select "Worker", and submit. | User redirected to Login page with a success message. |
| 1.3 | Try to register with non-matching passwords. | Error message displayed; registration blocked. |

## 2. Access Control & Role Assignment
| Step | Action | Expected Result |
| :--- | :--- | :--- |
| 2.1 | Log in with the account created in Step 1.2. | Dashboard loads correctly. |
| 2.2 | Check the Sidebar for "Admin Panel" or "Audit Logs". | **Links are HIDDEN.** Standard users should not see administrative tools. |
| 2.3 | Manually navigate to `/admin-panel/`. | **403 Forbidden** or **Permission Denied** error (via `SuperAdminRequiredMixin`). |
| 2.4 | Log in with a Super Admin account (Role ID 1). | **"Admin Panel"** and **"Audit Logs"** links are visible and accessible. |

## 3. Login Audit Logs
| Step | Action | Expected Result |
| :--- | :--- | :--- |
| 3.1 | As a Super Admin, navigate to **System > Audit Logs**. | List of recent logins displayed with IP Address, Time, and Status. |
| 3.2 | Perform a login on a different device/browser. | A new entry appears in the Audit Logs with the correct **User Agent** and **IP**. |
| 3.3 | Use the "User" filter to select a specific staff member. | List narrows down to only that user's login history. |
| 3.4 | Filter by a date range where no logins occurred. | "No login logs found" informative message displayed. |

## 4. UI Appearance (Off-White Theme)
| Step | Action | Expected Result |
| :--- | :--- | :--- |
| 4.1 | Log in and view the main Dashboard in **Light Mode**. | Background is soft off-white (`#F8F9FA`), cards have subtle contrast against the background. |
| 4.2 | Toggle to **Dark Mode**. | Background switches to deep slate; off-white logic does not affect dark theme readability. |

## 5. Session Management (Logout)
| Step | Action | Expected Result |
| :--- | :--- | :--- |
| 5.1 | Click the **"Log Out"** link in the sidebar. | System performs a POST request and terminates the session. |
| 5.2 | Verify redirection. | User is redirected back to the Login page. |
| 5.3 | Navigate back to `/` using the browser's back button or URL. | User remains logged out and is prompted to log in again (Login Required). |

---

> [!IMPORTANT]
> **Verification on Azure**: After pushing changes, ensure the GitHub Actions build succeeds. The `startup.sh` will auto-run `python manage.py migrate`, so no manual DB intervention should be required to test the Audit Log model.
