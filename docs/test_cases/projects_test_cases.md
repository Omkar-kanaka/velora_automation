# Functional Test Cases: Projects & Workflow Management

- **Functional Area:** New Project Creation, Context Inputs (FRDs, Meeting Notes, Git Repos) & Projects List
- **Test Suite References:**
  - [`tests/projects/test_new_project.py`](../../tests/projects/test_new_project.py) (`PROJ-01` to `PROJ-12`)
  - [`tests/projects/test_projects_list.py`](../../tests/projects/test_projects_list.py) (`LIST-01` to `LIST-03`)
- **Pytest Markers:** `@pytest.mark.projects`, `@pytest.mark.projects_list`, `@pytest.mark.smoke`, `@pytest.mark.regression`
- **Total Test Cases:** 15

---

## 1. New Project & Context Inputs (`PROJ`)

| ID | Priority | Type | Scenario | Steps | Expected Result | Automation Status | Automated Test Function | Linked Bug |
| :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| `PROJ-01` | P0 | UI | Start button disabled when prompt is empty | 1. Sign in and land on `/app`<br>2. Inspect **Start** button before typing<br>3. Type a brief prompt into textarea<br>4. Clear the textarea | **Start** is disabled when empty, becomes enabled when text is entered, and disables again when cleared. | Automated (Smoke) | `test_start_button_state_follows_prompt_input` | - |
| `PROJ-02` | P1 | Positive | Select an example prompt shortcut | 1. On `/app`, click **Quick product discovery** (also test **Partner self-serve onboarding** / **Fix duplicate order emails**) | Prompt textarea populates and **Start** becomes enabled. | Automated (Regression) | `test_example_prompt_populates_textarea_and_enables_start` | - |
| `PROJ-03` | P1 | Positive | Add meeting notes via modal | 1. Click **Add notes, docs or code** -> **Paste meeting notes**<br>2. Fill **Title** and **Notes**<br>3. Click **Add notes** | Modal closes and meeting notes appear attached as context chip on `/app`. | Automated (Regression) | `test_add_meeting_notes_attaches_context_chip` | - |
| `PROJ-04` | P2 | UI | Cancel meeting notes modal discards input | 1. Open **Paste meeting notes** modal<br>2. Type sample Title/Notes<br>3. Click **Cancel** | Modal closes and no context attachment is added. | Automated (Regression) | `test_cancel_meeting_notes_modal_discards_input` | - |
| `PROJ-05` | P2 | Negative | Submit empty meeting notes modal | 1. Open **Paste meeting notes** modal<br>2. Leave Title/Notes blank and inspect submit button | Add notes button remains disabled. | Automated (Regression) | `test_empty_meeting_notes_keeps_submit_disabled` | - |
| `PROJ-06` | P1 | Positive | Add a public repository via modal | 1. Click **Add notes, docs or code** -> **Add a repository**<br>2. Enter **Repository link**, **Branch** (`main`), select **Public**<br>3. Click **Add repository** | Modal closes and repository appears attached as context chip. | Automated (Regression) | `test_add_public_repository_attaches_context_chip` | - |
| `PROJ-07` | P1 | Positive | Add a private repository option toggle | 1. Open **Add a repository** modal<br>2. Select **Private** radio option | Access token input field expands cleanly and private option is selected. | Automated (Regression) | `test_repository_private_radio_reveals_access_token_field` | - |
| `PROJ-08` | P2 | Negative | Invalid repository URL or Cancel discards input | 1. Open **Add a repository** modal<br>2. Enter invalid URL (`invalid-url`) -> inspect error<br>3. Click **Cancel** | Validation error displays and Cancel closes modal without adding context. | Automated (Regression) | `test_repository_invalid_url_shows_validation_and_cancel_discards` | - |
| `PROJ-09` | P1 | Positive | Upload valid document (`.md`, `.pdf`, `.docx`) | 1. Click **Add notes, docs or code** -> **Upload an FRD or document**<br>2. Upload a valid sample `.md` or `.pdf` file | File uploads cleanly and appears attached as context chip on `/app`. | Automated (Regression) | `test_upload_valid_frd_documents_attaches_context` | - |
| `PROJ-10` | P2 | Negative | Reject unsupported file format on upload | 1. Trigger document upload with an unsupported file (e.g., `.png` image) | App displays an error alert rejecting unsupported file type. | Automated (Regression) | `test_upload_unsupported_file_format_displays_error_alert` | - |
| `PROJ-11` | P0 | Positive | Create a new project from prompt (End-to-End) | 1. On `/app`, enter a unique project description<br>2. Click **Start** | Project creation succeeds, transitions into the clarification/run setup view, and project is persisted. | Automated (Smoke / E2E) | `test_start_project_with_prompt_opens_run_setup_step` | - |
| `PROJ-12` | P1 | Positive | Create a new project with prompt + attached context | 1. On `/app`, attach meeting notes or a `.md` document<br>2. Enter a prompt and click **Start** | Project starts successfully with attached context chips preserved in run setup. | Automated (Regression) | `test_start_project_with_prompt_and_attached_context_preserves_state` | - |

---

## 2. Projects List & Details (`LIST`)

| ID | Priority | Type | Scenario | Steps | Expected Result | Automation Status | Automated Test Function | Linked Bug |
| :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| `LIST-01` | P1 | UI | Empty state displays when no projects exist | 1. With a fresh account/empty project list, open `/app/projects` | Displays empty state notice and a **Start a new project** CTA navigating to `/app`. | Automated (Regression) | `test_projects_empty_state_and_start_cta_for_new_account` | - |
| `LIST-02` | P0 | Positive | Newly created project appears in Projects list & sidebar badge | 1. Create a project on `/app`<br>2. Navigate to **All projects** (`/app/projects`) | New project is visible in the list and the sidebar **All projects** count badge increments by 1. | Automated (Smoke) | `test_newly_created_project_appears_in_list_and_increments_sidebar_badge` | - |
| `LIST-03` | P1 | Positive | Open an existing project from Projects list | 1. On `/app/projects`, click an existing project card/item | Opens that project's detail/run screen with its saved title and configuration intact. | Automated (Regression) | `test_opening_existing_project_navigates_to_project_detail` | - |
