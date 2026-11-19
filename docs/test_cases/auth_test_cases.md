# Functional Test Cases: Authentication & Session Management

- **Functional Area:** Authentication, Registration, Password Management & Route Security
- **Test Suite Reference:** [`tests/auth/test_auth.py`](../../tests/auth/test_auth.py)
- **Pytest Markers:** `@pytest.mark.auth`, `@pytest.mark.smoke`, `@pytest.mark.regression`, `@pytest.mark.security`
- **Total Test Cases:** 15

---

## Test Cases Matrix

| ID | Priority | Type | Scenario | Steps | Expected Result | Automation Status | Automated Test Function | Linked Bug |
| :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| `AUTH-01` | P0 | Positive | Sign in with valid credentials | 1. Open `/sign-in`<br>2. Enter valid Work email & Password<br>3. Click **Sign in** | User is authenticated and redirected to `/app` ("What are you building?"). | Automated (Smoke) | `test_sign_in_with_valid_credentials_redirects_to_app` | - |
| `AUTH-02` | P0 | Positive | Sign out from authenticated session | 1. While signed in, open user profile menu in sidebar<br>2. Click **Sign out** | Session is cleared; user is redirected to `/sign-in`. | Automated (Smoke) | `test_sign_out_clears_session_and_redirects_to_sign_in` | - |
| `AUTH-03` | P0 | Security | Protected routes block unauthenticated access | 1. Clear session/cookies<br>2. Navigate directly to `/app`, `/app/projects`, and `/app/settings` | Each route redirects the user to `/sign-in`. | Automated (Smoke) | `test_protected_routes_redirect_unauthenticated_user_to_sign_in` | - |
| `AUTH-04` | P1 | Negative | Sign in with wrong password | 1. Open `/sign-in`<br>2. Enter valid email (`test@ok.com`) and invalid password<br>3. Click **Sign in** | Login fails; error toast/message is displayed and user stays on `/sign-in`. | Automated (Regression) | `test_sign_in_with_wrong_password_displays_error` | - |
| `AUTH-05` | P1 | Negative | Sign in with unregistered email | 1. Open `/sign-in`<br>2. Enter non-existent email and any password<br>3. Click **Sign in** | Login fails; error message/toast is shown and user stays on `/sign-in`. | Automated (Regression) | `test_sign_in_with_unregistered_email_displays_error` | - |
| `AUTH-06` | P2 | Negative | Sign in with empty fields or invalid email format | 1. Open `/sign-in`<br>2. Leave fields empty (or enter `not-an-email`) and click **Sign in** | Form validation prevents submission and highlights invalid/required fields. | Automated (Regression) | `test_sign_in_blocks_empty_and_invalid_email_submission` | - |
| `AUTH-07` | P2 | UI | Toggle password visibility on Sign In | 1. Enter text in **Password**<br>2. Click **Show** toggle<br>3. Click **Hide** toggle | Input `type` switches from `password` to `text` and back to `password`. | Automated (Regression) | `test_password_visibility_toggle_switches_input_type` | - |
| `AUTH-08` | P1 | Positive | Navigate between auth pages | 1. On `/sign-in`, click **Sign up**<br>2. Click **Sign in**<br>3. Click **Forgot password?**<br>4. Click **Back to sign in** | Routes transition cleanly: `/sign-in` -> `/sign-up` -> `/sign-in` -> `/forgot-password` -> `/sign-in`. | Automated (Regression) | `test_navigation_links_between_auth_screens` | - |
| `AUTH-09` | P1 | Positive | Sign up with valid new account | 1. Open `/sign-up`<br>2. Enter unique work email<br>3. Enter strong password matching all 4 rules & confirm password<br>4. Click **Create account** | Account is created and user proceeds to onboarding/app (or confirmation state). | Automated (Regression) | `test_sign_up_with_valid_new_account_succeeds` | - |
| `AUTH-10` | P1 | Negative | Sign up with already registered email | 1. Open `/sign-up`<br>2. Enter `test@ok.com` and a valid strong password<br>3. Click **Create account** | Error message/toast indicates account already exists; duplicate account is not created. | Automated (Regression) | `test_sign_up_with_existing_email_displays_error` | - |
| `AUTH-11` | P2 | UI/Negative | Sign up password strength checklist & mismatch validation | 1. Open `/sign-up`<br>2. Type passwords failing each rule (`<8 chars`, no uppercase, no number, no symbol)<br>3. Enter mismatched **Confirm password** | Checklist dynamically reflects met/unmet rules; mismatched confirm password blocks submission with validation feedback. | Automated (Regression) | `test_sign_up_password_rules_and_mismatch_validation` | - |
| `AUTH-12` | P2 | Positive | Forgot password request submission with valid email | 1. Open `/forgot-password`<br>2. Enter valid registered work email (`test@ok.com`)<br>3. Click **Send reset link** | Password reset API (`accounts:sendOobCode`) returns `200`; UI advances to Step 2 (**Check your inbox**) displaying email, generic notice, **Change**, and **resend the link** controls. | Automated (Regression) | `test_forgot_password_submission_shows_confirmation_step` | `VEL-025` |
| `AUTH-13` | P1 | Positive | Session persists across browser refresh | 1. Sign in to `/app`<br>2. Reload the page (`F5`) | User remains authenticated on `/app` without redirecting to `/sign-in`. | Automated (Regression) | `test_authenticated_session_persists_across_page_reload` | - |
| `AUTH-14` | P2 | Negative | Forgot password blocks empty and malformed email | 1. Open `/forgot-password`<br>2. Submit blank email and then malformed email (`not-an-email`) | Inline validation displays `Enter your email.` / `Enter a valid email address.`; stays on Step 1 and does not call reset API. | Automated (Regression) | `test_forgot_password_blocks_empty_and_malformed_email` | `VEL-026` |
| `AUTH-15` | P2 | Security | Forgot password prevents user enumeration for unregistered email | 1. Open `/forgot-password`<br>2. Enter unregistered valid-format email<br>3. Click **Send reset link** | Reset API returns `200` and UI shows the same generic Step 2 notice (`If an account exists for this email, a reset link is on its way.`) without disclosing account existence. | Automated (Regression) | `test_forgot_password_unregistered_email_prevents_user_enumeration` | `VEL-026` |

---

## Linked Defect Traceability

| Bug ID | Severity / Priority | Status | Linked Test Cases | Automation & Verification Notes |
| :--- | :--- | :--- | :--- | :--- |
| `VEL-025` | Major - S2 / P1 - Blocker | Pending Fix | `AUTH-12` | UI + Firebase `accounts:sendOobCode` returns `HTTP 200` and loads Step 2, but actual reset email delivery to Inbox/Spam is not received. Automated test verifies UI transition; fix verification requires SMTP delivery check. |
| `VEL-026` | Medium - S3 / P2 - High | Pending Fix | `AUTH-14`, `AUTH-15` | Validates strict email format parsing and OWASP generic enumeration defense messaging (`"If an account exists for this email, a reset link is on its way."`). |
