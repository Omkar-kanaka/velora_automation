# Velora Automation Framework (Playwright + pytest + Python)

Robust end-to-end test automation framework for **Velora · AI Intelligence**, designed to treat a locally deployed instance (`http://localhost:5173`) as a dedicated QA environment while supporting seamless switching to remote QA, Staging, or Production environments.

---

## 1. Prerequisites

- **Python 3.12+**
- **Velora web app running locally** at `http://localhost:5173`
- **Playwright browsers** installed (`python -m playwright install chromium`)

---

## 2. First-Time Setup (Windows PowerShell)

1. **Create and activate the virtual environment**

   > On Windows PowerShell, allow script execution for the current process before activating `.venv`:

   ```powershell
   python -m venv .venv
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
   .\.venv\Scripts\Activate.ps1
   ```

2. **Install dependencies and Playwright browsers**

   ```powershell
   python -m pip install -r requirements.txt
   python -m playwright install chromium
   ```

3. **Review or update test user personas**

   User credentials and personas are stored in [`testdata/user.json`](testdata/user.json), organized by environment (`local_qa`, `qa`, `staging`, `prod`).
   Environment URLs and execution settings live in [`config/config.py`](config/config.py) and can be overridden via OS environment variables (`TEST_ENV`, `BASE_URL`, `BROWSER`, `HEADLESS`) or CLI flags.

---

## 3. Running Tests

Ensure your local Velora app is running first, then execute from the project root:

```powershell
# Run the full Auth suite
python -m pytest tests/auth/test_auth.py

# Run P0 Smoke tests only
python -m pytest -m smoke

# Run in headed mode (watch the browser at normal human speed — 600ms/action by default)
python -m pytest tests/auth/test_auth.py --headed

# Customize action speed in milliseconds (e.g., slower for demos or 0 for full speed)
python -m pytest tests/auth/test_auth.py --headed --slow-mo 800
python -m pytest tests/auth/test_auth.py --headed --slow-mo 0

# Run in parallel using pytest-xdist
python -m pytest tests/auth/test_auth.py -n auto

# Run against a different browser or environment
python -m pytest tests/auth/test_auth.py --browser-name firefox --env qa

# Run using system-installed Google Chrome or Microsoft Edge (e.g., if Windows Application Control blocks unsigned Chromium)
python -m pytest tests/auth/test_auth.py --browser-channel chrome --headed
```

---

## 4. Architecture & Design Standards

```text
velora_automation/
├── config/
│   └── config.py                  # Hierarchical env config (LocalQA/QA/Staging/Prod) + persona loader
├── core/
│   ├── api/
│   │   ├── api_client_interface.py # IApiClient interface (library-agnostic)
│   │   ├── playwright_api_client.py# Playwright APIRequestContext implementation
│   │   ├── request_builder.py      # Fluent RequestBuilder
│   │   ├── token_provider.py       # Cached OAuth2/Bearer TokenProvider
│   │   ├── abstract_service.py     # Base API service
│   │   └── health_service.py       # Pre-flight QA reachability check
│   └── factories/
│       ├── driver_factory.py       # Browser & isolated BrowserSession creation
│       └── login_factory.py        # Platform-extensible Login page factory
├── pages/
│   ├── base_page.py                # Resilient goto, loading settlement, Shadow DOM helpers
│   ├── dashboard_page.py           # /app page object
│   ├── auth/
│   │   ├── web_login_page.py       # /sign-in page object
│   │   ├── sign_up_page.py         # /sign-up page object
│   │   └── forgot_password_page.py # /forgot-password page object
│   └── components/
│       └── sidebar_component.py    # Global sidebar & user menu component
├── testdata/
│   └── user.json                   # Environment-scoped user personas & test credentials
├── tests/
│   └── auth/
│       └── test_auth.py            # AUTH-01 through AUTH-13 atomic test suite
├── utils/
│   ├── paths.py                    # Cross-platform pathlib.Path constants
│   ├── logger.py                   # Centralized structured logging
│   ├── artifact_capture.py         # Auto screenshot, console logs & DOM snapshots on failure
│   └── data_generator.py           # Unique test data generators
├── docs/
│   └── test_cases.md               # Living test case catalog (AUTH, NAV, PROJ, LIST, SET)
├── conftest.py                     # Windows Proactor policy, fixtures, failure hook
├── pytest.ini                      # Markers, logging, HTML report defaults
└── requirements.txt
```

### Core Engineering Guarantees
- **Strict POM Separation:** Page objects contain only locators and interactions (no assertions or `print()`); tests contain only flow orchestration and assertions.
- **Zero Flakiness:** Dynamic Playwright waits, loading indicator settlement (`wait_for_loading_settled()`), 3-attempt resilient navigation with `"load"` -> `"domcontentloaded"` fallback, and Shadow DOM support.
- **Atomic & Parallel-Safe:** Fresh isolated `BrowserContext` per test, indirect persona fixtures (`users`) backed by `testdata/user.json`, and unique generated emails for signup flows.
- **Automatic Failure Diagnostics:** Every failed test automatically captures:
  - Full-page screenshot -> `artifacts/screenshots/`
  - Browser `console.error`, `console.warn`, and `pageerror` logs -> `artifacts/console_logs/`
  - Structural DOM snapshot (URL, title, visible modals, full HTML) -> `artifacts/failure_dom/`
  - Self-contained HTML report -> `reports/report.html`
