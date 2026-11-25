# Functional Test Cases: Runs & Workflow Lifecycle

- **Functional Area:** End-to-End Run Lifecycle (Step 1 Composer, Step 2 Run Setup, Stage 1 Kickoff, Stage 2 Pick my Brain, Stage 3 Specs In-Progress & 10-File Review, Download, Request Changes Drawer, and Stage 4 Delivery)
- **Test Suite References:**
  - [`tests/projects/test_run_workflow.py`](../../tests/projects/test_run_workflow.py) (`RUN-01` to `RUN-11`, `RUN-E2E`)
- **Pytest Markers:** `@pytest.mark.projects`, `@pytest.mark.workflow`, `@pytest.mark.smoke`, `@pytest.mark.ui`
- **Total Test Cases:** 16

---

## Run Workflow Lifecycle (`RUN`)

| ID | Priority | Type | Scenario | Steps | Expected Result | Automation Status | Automated Test Function | Linked Bug |
| :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| `RUN-01` | P0 | Positive / E2E | Setup run with full HMS prompt & FRD document | 1. Enter full Hospital Management System prompt on `/app`<br>2. Upload `Test_Hospital_Management_System_FRD (1).pdf`<br>3. Click **Start**<br>4. Enter Project Name & pick End Date (Jan 30, 2027)<br>5. Click **Start the run** | Run setup submits, 'Getting it ready' checklist finishes (description read, FRD read, first question prepared), and 'Your first question is ready' blue card appears with **Start answering** button. | Automated (Smoke) | `test_create_hms_run_and_settle_getting_it_ready` | - |
| `RUN-02` | P0 | UI | Transition to Stage 2 & verify Stepper | 1. Click **Start answering**<br>2. Inspect `/questions` layout | URL navigates to `/questions`. Stepper displays Step 1 (Setup: Done) and Step 2 (Pick my Brain: Active). Active question card renders heading and 'Waiting for you' badge. | Automated (Smoke) | `test_complete_hms_run_workflow_lifecycle_e2e` | - |
| `RUN-03` | P0 | Positive | Suggested answer chip populates textarea | 1. On active question card, click **💡 Suggested: ...** chip<br>2. Inspect question textarea | Clicking suggested chip copies the recommendation into the textarea cleanly and enables **Submit answer**. | Automated (Smoke) | `test_complete_hms_run_workflow_lifecycle_e2e` | - |
| `RUN-04` | P0 | Positive / Dynamic | Dynamic Q&A loop through all clarification questions | 1. Submit answer for current question<br>2. Loop through dynamic questions clicking suggested answer chips or domain fallbacks<br>3. Continue until all questions are answered | Application transitions to completion card: **That's everything for now - We have what we need to write the specs.** with **Continue to Specs** CTA. | Automated (Smoke) | `test_complete_hms_run_workflow_lifecycle_e2e` | - |
| `RUN-05` | P1 | UI | Expand and collapse 'Answered so far' accordion | 1. On completion card, inspect **Answered so far (<N>)** badge<br>2. Click **Hide** / **Show** toggle button | Past questions and user answers expand/collapse smoothly without page reloads. | Automated (Regression) | `test_complete_hms_run_workflow_lifecycle_e2e` | - |
| `RUN-06` | P0 | Negative / UI | Stage 3 in-progress generation & drawer restrictions | 1. Click **Continue to Specs**<br>2. Inspect `/specs` during generation | Stepper shows Step 3: 'Writing the specs...'. **Continue to Delivery** is disabled. Clicking **Request changes** opens side drawer with disabled textarea ('Updating the specs...') and disabled **Send** button. | Automated (Smoke) | `test_complete_hms_run_workflow_lifecycle_e2e` | - |
| `RUN-07` | P0 | Positive | Specs generation settlement | 1. Wait dynamically for specs writing to complete | Stepper updates to Step 3: 'Ready for your review', generated timestamp displays, and **Continue to Delivery** becomes enabled. | Automated (Smoke) | `test_complete_hms_run_workflow_lifecycle_e2e` | - |
| `RUN-08` | P0 | Positive / Verification | **Exhaustive 10-File Specification Review** | 1. Sequentially click each of the 10 specification tabs (`specification.md`, `ui_design.md`, `hld.md`, `pm.md`, `infra.md`, `lld.md`, `e2e_testing.md`, `frontend_testing.md`, `backend_testing.md`, `design_patterns.md`) | Each tab activates, displays selected pill state, URL updates with `?file=<tab>`, and preview renders non-empty markdown containing Hospital Management System keywords. | Automated (Smoke) | `test_complete_hms_run_workflow_lifecycle_e2e` | - |
| `RUN-09` | P1 | Positive | Specification download flow | 1. On `/specs`, click **Download ⌄**<br>2. Intercept browser download event | File download initiates cleanly, saving the specifications archive (`.zip` / `.md`) locally without network errors. | Automated (Regression) | `test_complete_hms_run_workflow_lifecycle_e2e` | - |
| `RUN-10` | P1 | Positive | Request changes drawer in ready state | 1. When specs are ready, click **Request changes**<br>2. Enter modification feedback into now-enabled textarea<br>3. Inspect **Send** button<br>4. Click close (**X**) | Drawer displays editable input and enabled **Send** button. Closing the drawer dismisses it without unpersisted mutations. | Automated (Regression) | `test_complete_hms_run_workflow_lifecycle_e2e` | - |
| `RUN-11` | P0 | Positive | Advance to Stage 4 (Delivery) | 1. On `/specs`, click **Continue to Delivery** | Application advances to Step 4: Delivery, and stepper/URL updates to reflect delivery phase. | Automated (Smoke) | `test_complete_hms_run_workflow_lifecycle_e2e` | - |

---

## Project New Run Iteration Lifecycle (`RUN-NEW`)

- **Functional Area:** Iterative Run Creation inside an existing project (`/app/projects/:id` -> `/app/projects/:id/runs/new`).
- **Test Suite Reference:** [`tests/projects/test_project_new_run.py`](../../tests/projects/test_project_new_run.py)

| ID | Priority | Type | Scenario | Steps | Expected Result | Automation Status | Automated Test Function | Linked Bug |
| :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| `RUN-NEW-01` | P0 | Positive / UI | Header 'New run' Button & Empty Runs State Verification | 1. Open an existing project detail page (`/app/projects/:id`)<br>2. Verify empty state 'No runs yet.' label and outline **New run** button<br>3. Click header **New run** button<br>4. Inspect composer layout | Navigates to `/runs/new`. Heading renders `What's changed in <project_name>?`. Textarea displays placeholder. Start Run button is disabled. | Automated (Regression) | `test_new_run_navigation_and_composer_layout` | - |
| `RUN-NEW-01B` | P0 | Positive / UI | Empty State 'No runs yet. [New run]' Button Navigation | 1. Open an existing project detail page with 0 runs<br>2. Click the outline **New run** button inside the empty runs section<br>3. Inspect composer layout | Navigates to `/runs/new` identically to the header action. Heading renders `What's changed in <project_name>?` with empty disabled prompt. | Automated (Regression) | `test_empty_state_new_run_button_navigates_to_composer` | - |
| `RUN-NEW-02` | P1 | Positive / Validation | Prompt Entry Validation & 'Start Run' Button State | 1. Navigate to `/runs/new`<br>2. Verify **Start Run <N>** is disabled<br>3. Type prompt text<br>4. Clear prompt text | Button enables upon entering text, and disables again when cleared. | Automated (Regression) | `test_new_run_prompt_entry_enables_start_run_button` | - |
| `RUN-NEW-03` | P1 | Positive | Context Attachment Menu on New Run | 1. On `/runs/new`, click **+ Add notes, docs or code**<br>2. Select **Paste meeting notes**<br>3. Enter title and body, click **Add notes** | Context menu opens smoothly. Meeting notes modal saves context and renders a chip badge on the composer. | Automated (Regression) | `test_new_run_context_attachment_menu_options` | - |
| `RUN-NEW-04` | P0 | Positive / E2E | End-to-End New Run Kickoff & Question Lifecycle | 1. On `/runs/new`, enter prompt and click **Start Run <N>**<br>2. Await 'Getting it ready' checklist settlement<br>3. Click **Start answering** | Run transitions through kickoff preparation, blue readiness card appears, and clicking **Start answering** advances to dynamic questions. | In Progress | `test_new_run_kickoff_advances_to_workflow` | - |

