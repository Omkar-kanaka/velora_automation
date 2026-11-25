"""End-to-End Run Workflow Lifecycle Test Suite — RUN-01 through RUN-11.

Covers:
- Step 1 & 2: Hello World Web Application Prompt (no FRD document) + Timeline configuration.
- Stage 1 Kickoff: 'Getting it ready' checklist settlement ➔ 'Start answering' card.
- Stage 2 (Pick my Brain): Dynamic Q&A loop using suggested chips until completion.
- Stage 3 (Specs In-Progress): 'Writing the specs...' state, disabled delivery, restricted 'Spec changes' drawer.
- Stage 3 (Specs Ready): 'Ready for your review', exhaustive 10-file verification, download, request changes.
- Stage 4 (Delivery): Transition via 'Continue to Delivery'.
"""

import time
from typing import Any

import pytest

from config.config import UserCredentials
from pages.projects.new_project_page import NewProjectPage
from pages.projects.run_questions_page import RunQuestionsPage
from pages.projects.run_specs_page import RunSpecsPage


@pytest.mark.smoke
@pytest.mark.projects
@pytest.mark.workflow
@pytest.mark.ui
@pytest.mark.tc("RUN-E2E")
@pytest.mark.parametrize("users", ["valid_user"], indirect=True)
def test_complete_hms_run_workflow_lifecycle_e2e(
    authenticated_user: UserCredentials,
    new_project_page: NewProjectPage,
    run_questions_page: RunQuestionsPage,
    run_specs_page: RunSpecsPage,
    project_test_data: dict[str, Any],
    track_and_cleanup_project: Any,
) -> None:
    """RUN-01 through RUN-11: Full End-to-End Hello World Run Lifecycle without FRD attachment."""
    workflow_data = project_test_data.get("hello_world_workflow") or project_test_data["hms_workflow"]

    # ------------------------------------------------------------------
    # RUN-01: Setup & Kickoff Checklist Settle (Prompt only, no FRD)
    # ------------------------------------------------------------------
    new_project_page.open()
    new_project_page.enter_prompt(workflow_data["prompt"])
    assert new_project_page.is_start_button_enabled()

    new_project_page.click_start()
    new_project_page.wait_for_step_two_loaded()

    unique_project_name = f"{workflow_data['project_name_prefix']} {int(time.time())}"
    new_project_page.enter_project_name(unique_project_name)
    new_project_page.select_end_date()
    assert new_project_page.is_start_run_button_enabled()

    new_project_page.click_start_the_run()
    new_project_page.wait_for_getting_it_ready_settled(timeout_ms=60000)
    assert new_project_page.is_start_answering_visible()
    track_and_cleanup_project(new_project_page.get_created_project_id())

    # Transition into Stage 2
    new_project_page.click_start_answering()
    run_questions_page.wait_until_loaded(timeout_ms=15000)

    # ------------------------------------------------------------------
    # RUN-02: Stage 2 Stepper & Active Question Verification
    # ------------------------------------------------------------------
    assert run_questions_page.has_unanswered_question()
    initial_question = run_questions_page.get_current_question_text()
    assert len(initial_question) > 5

    # ------------------------------------------------------------------
    # RUN-03 & RUN-04: Dynamic Q&A Loop using Suggested Chips to Completion
    # ------------------------------------------------------------------
    run_questions_page.answer_all_questions_dynamically(max_rounds=35)
    assert run_questions_page.is_completion_card_visible(timeout_ms=20000)

    # ------------------------------------------------------------------
    # RUN-05: 'Answered so far' Accordion Toggle
    # ------------------------------------------------------------------
    run_questions_page.toggle_answered_accordion()

    # ------------------------------------------------------------------
    # RUN-06: Transition to Specs & In-Progress Verification
    # ------------------------------------------------------------------
    run_questions_page.click_continue_to_specs()
    run_specs_page.wait_until_loaded(timeout_ms=20000)

    # Check in-progress constraints if generation is still underway
    if run_specs_page.is_writing_specs(timeout_ms=5000):
        assert run_specs_page.is_continue_to_delivery_disabled()
        assert run_specs_page.is_request_changes_button_disabled(), (
            "Expected 'Request changes' button to be disabled while specs are actively generating"
        )

    # ------------------------------------------------------------------
    # RUN-07: Wait for Specs Generation to Settle (Ready for your review)
    # ------------------------------------------------------------------
    run_specs_page.wait_for_specs_ready(timeout_ms=6000000)
    assert run_specs_page.is_ready_for_review()
    assert run_specs_page.is_continue_to_delivery_enabled()

    # ------------------------------------------------------------------
    # RUN-08: Exhaustive 10-File Specification Opening & Content Check
    # ------------------------------------------------------------------
    expected_tabs = workflow_data["expected_specs_tabs"]
    assert len(expected_tabs) == 10

    for tab_name in expected_tabs:
        assert run_specs_page.is_tab_visible(tab_name), f"Tab '{tab_name}' not visible in specs bar."
        run_specs_page.select_tab(tab_name)

        preview_text = run_specs_page.get_document_preview_text()
        assert len(preview_text) > 50, f"Specification document '{tab_name}' preview is unexpectedly empty."

        # Check for domain presence in specifications
        has_domain_term = any(
            kw.lower() in preview_text.lower() for kw in workflow_data["domain_verification_keywords"]
        )
        assert has_domain_term, f"Domain keywords missing in document '{tab_name}'"

    # ------------------------------------------------------------------
    # RUN-09: Download Flow Automation
    # ------------------------------------------------------------------
    downloaded_file = run_specs_page.trigger_download(timeout_ms=15000)
    assert downloaded_file.suggested_filename != ""
    assert any(
        downloaded_file.suggested_filename.endswith(ext) for ext in [".zip", ".md", ".tar.gz", ".json"]
    )

    # ------------------------------------------------------------------
    # RUN-10: Request Changes Flow (Completed / Ready State)
    # ------------------------------------------------------------------
    assert run_specs_page.is_request_changes_button_enabled(), (
        "Expected 'Request changes' button to become enabled after specs generation completed"
    )
    run_specs_page.open_request_changes_drawer()
    assert run_specs_page.is_request_changes_drawer_open()
    assert not run_specs_page.is_drawer_textarea_disabled()

    run_specs_page.enter_request_changes_feedback(workflow_data["request_changes"]["sample_feedback"])
    assert not run_specs_page.is_drawer_send_button_disabled()
    run_specs_page.close_request_changes_drawer()
    assert not run_specs_page.is_request_changes_drawer_open()

    # ------------------------------------------------------------------
    # RUN-11: Advance to Stage 4 (Delivery)
    # ------------------------------------------------------------------
    run_specs_page.click_continue_to_delivery()
    assert "delivery" in run_specs_page.page.url.lower() or run_specs_page.is_locator_visible(
        run_specs_page.page.locator("text='Delivery'").first, timeout_ms=5000
    )
