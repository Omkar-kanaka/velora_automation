# Velora Web App — Test Case Management Catalog

Welcome to the Velora QA Test Case Catalog. The test suite is organized into **3 functional domain files** mapped directly to the automated test suites in `tests/`.

---

## 📁 Functional Test Suites

| # | Functional Document | Scope / Features Covered | Test IDs | Count | Automation Suite |
| :-: | :--- | :--- | :--- | :-: | :--- |
| **1** | [**`auth_test_cases.md`**](./auth_test_cases.md) | Sign-In, Sign-Out, Session Persistence, Route Guards, Sign-Up, Forgot Password & Defects (`VEL-025`, `VEL-026`) | `AUTH-01` to `AUTH-15` | 15 | [`tests/auth/test_auth.py`](../../tests/auth/test_auth.py) |
| **2** | [**`projects_test_cases.md`**](./projects_test_cases.md) | New Project creation, Prompt inputs, Context attachments (Notes, GitHub repos, FRD docs), Projects List | `PROJ-01` to `PROJ-12`<br>`LIST-01` to `LIST-03` | 15 | [`tests/projects/test_new_project.py`](../../tests/projects/test_new_project.py)<br>[`tests/projects/test_projects_list.py`](../../tests/projects/test_projects_list.py) |
| **3** | [**`platform_and_settings_test_cases.md`**](./platform_and_settings_test_cases.md) | Sidebar navigation, icon-rail mode, Settings (Database, Storage, AI Model) connection tests | `NAV-01` to `NAV-02`<br>`SET-01` to `SET-07` | 9 | [`tests/navigation/test_navigation.py`](../../tests/navigation/test_navigation.py)<br>[`tests/settings/test_settings.py`](../../tests/settings/test_settings.py) |
| | **Total** | | | **39** (36 Core + Sub-flows) | **100% Automated** |

---

## 🎯 Priority Distribution

- **P0 (Smoke):** 8 test cases — Critical user paths executed on every PR/build.
- **P1 (Core Functional):** 15 test cases — Primary user journeys, modals, inputs, and happy paths.
- **P2 (Negative / Edge / UI):** 13 test cases — Validation rules, boundary cases, error toasts, and UI states.

---

## 🛠️ Excel Export on Demand

To compile all 3 functional Markdown files into a styled multi-tab Excel workbook for management or stakeholders:

```bash
# Run from repository root
python utils/export_testcases_to_excel.py
```

The resulting file is saved at `reports/velora_test_cases.xlsx` (ignored by Git to keep the repository clean).

---

## 🌿 Git Version-Control Guidelines

1. **Native Text Diffs:** Every test case is stored in pure Markdown tables. Pull requests will show clear line-by-line diffs (`+` added, `-` deleted).
2. **Zero Merge Conflicts:** Teammates working on different functional domains (e.g., Auth vs. Projects) edit separate `.md` files without colliding.
3. **Execution Artifact Isolation:** Automated test results and temporary Excel locks are ignored in `.gitignore`, keeping your Git commits 100% clean.
