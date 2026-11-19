# Functional Test Cases: Platform Navigation & Settings

- **Functional Area:** Global App Shell, Sidebar Navigation & Configuration Settings (Database, Storage, AI Model)
- **Test Suite References:**
  - [`tests/navigation/test_navigation.py`](../../tests/navigation/test_navigation.py) (`NAV-01` to `NAV-02`)
  - [`tests/settings/test_settings.py`](../../tests/settings/test_settings.py) (`SET-01` to `SET-07`)
- **Pytest Markers:** `@pytest.mark.nav`, `@pytest.mark.settings`, `@pytest.mark.smoke`, `@pytest.mark.regression`, `@pytest.mark.ui`
- **Total Test Cases:** 9

---

## 1. Navigation & Application Shell (`NAV`)

| ID | Priority | Type | Scenario | Steps | Expected Result | Automation Status | Automated Test Function | Linked Bug |
| :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| `NAV-01` | P0 | Positive | Navigate across primary sections via sidebar | 1. Sign in to `/app`<br>2. Click **All projects**<br>3. Open user menu -> click **Settings**<br>4. Click **New project** | Each route loads its matching heading (`Projects`, `Settings`, `What are you building?`) without page/console errors. | Automated (Smoke) | `test_sidebar_navigates_across_primary_sections_without_errors` | - |
| `NAV-02` | P2 | UI | Collapse and expand sidebar via button and shortcut | 1. Click sidebar collapse toggle (or press `Ctrl+B`)<br>2. Verify icon-rail mode<br>3. Click expand toggle (or press `Ctrl+B`) | Sidebar toggles cleanly between expanded and collapsed states; navigation remains functional in both modes. | Automated (Regression) | `test_sidebar_collapse_and_expand_via_button_and_shortcut` | - |

---

## 2. System Settings & Integrations (`SET`)

| ID | Priority | Type | Scenario | Steps | Expected Result | Automation Status | Automated Test Function | Linked Bug |
| :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| `SET-01` | P0 | UI | Settings page displays Database, AI model, and Storage cards | 1. Open `/app/settings` | All 3 cards (**Database**, **AI model**, **Storage**) render with active status and configuration values. | Automated (Smoke) | `test_settings_displays_database_ai_model_and_storage_sections` | - |
| `SET-02` | P1 | UI | Database Edit form expands and Cancel restores view | 1. In **Database**, click **Edit**<br>2. Modify a field (e.g., Port) without saving<br>3. Click **Cancel** | Form collapses and original DB connection string remains unchanged. | Automated (Regression) | `test_database_edit_form_expands_and_cancel_restores_summary` | - |
| `SET-03` | P1 | Positive | Database Test connection succeeds with valid local config | 1. In **Database**, click **Edit**<br>2. Click **Test connection** with valid local DB settings | Success status notification confirms database connectivity. | Automated (Regression) | `test_database_test_connection_returns_status_feedback` | - |
| `SET-04` | P2 | Negative | Database Test connection fails with invalid host/port | 1. In **Database**, click **Edit**<br>2. Enter invalid port (`9999`)<br>3. Click **Test connection**<br>4. Click **Cancel** | Error feedback indicates connection failure; clicking Cancel keeps live config intact. | Automated (Regression) | `test_database_test_connection_fails_with_invalid_port_and_cancel_preserves_config` | - |
| `SET-05` | P1 | UI | Storage Edit form expands and Cancel restores view | 1. In **Storage**, click **Edit**<br>2. Modify **Path** without saving<br>3. Click **Cancel** | Form collapses and original local storage path remains unchanged. | Automated (Regression) | `test_storage_edit_form_expands_and_cancel_restores_summary` | - |
| `SET-06` | P1 | Positive | Storage Test connection succeeds with valid local path | 1. In **Storage**, click **Edit**<br>2. Click **Test connection** with valid storage path | Success status notification confirms storage directory is accessible. | Automated (Regression) | `test_storage_test_connection_succeeds_with_valid_local_path` | - |
| `SET-07` | P2 | Negative | Storage Test connection handles invalid path | 1. In **Storage**, click **Edit**<br>2. Enter an invalid/non-existent path<br>3. Click **Test connection**<br>4. Click **Cancel** | Error feedback is shown; Cancel keeps existing valid storage config untouched. | Automated (Regression) | `test_storage_test_connection_fails_with_invalid_path_and_cancel_preserves_config` | - |
