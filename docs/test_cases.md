# Velora Web App — Test Case Catalog

> [!NOTE]
> The test case catalog has been organized into **3 functional domain files** under [`docs/test_cases/`](./test_cases/README.md) for streamlined maintenance, modular ownership, and clean Git collaboration.

## Quick Links to Functional Files

1. [**Authentication & Session Management** (`AUTH-01` to `AUTH-15`)](./test_cases/auth_test_cases.md)
   - Scope: Sign-In, Sign-Out, Session Persistence, Route Protection, Sign-Up, Forgot Password, and Bug Traceability (`VEL-025`, `VEL-026`).
   - Automation: [`tests/auth/test_auth.py`](../tests/auth/test_auth.py)

2. [**Projects & Workflow Management** (`PROJ-01` to `PROJ-12`, `LIST-01` to `LIST-03`)](./test_cases/projects_test_cases.md)
   - Scope: New Project creation, prompt inputs, context uploads (FRD docs, meeting notes, git repos), and projects list.
   - Automation: [`tests/projects/test_new_project.py`](../tests/projects/test_new_project.py) and [`tests/projects/test_projects_list.py`](../tests/projects/test_projects_list.py)

3. [**Platform Navigation & Settings** (`NAV-01` to `NAV-02`, `SET-01` to `SET-07`)](./test_cases/platform_and_settings_test_cases.md)
   - Scope: Sidebar shell navigation, collapsible rail, and configuration settings (Database, Storage, AI model).
   - Automation: [`tests/navigation/test_navigation.py`](../tests/navigation/test_navigation.py) and [`tests/settings/test_settings.py`](../tests/settings/test_settings.py)

---

## Excel Export Utility

To generate an Excel workbook (`reports/velora_test_cases.xlsx`) compiled from all functional markdown files:

```bash
python utils/export_testcases_to_excel.py
```
