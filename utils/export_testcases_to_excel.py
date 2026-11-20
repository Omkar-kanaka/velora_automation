"""Utility to compile modular Markdown test cases into a styled Excel workbook."""

import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_TC_DIR = PROJECT_ROOT / "docs" / "test_cases"
REPORTS_DIR = PROJECT_ROOT / "reports"
OUTPUT_EXCEL = REPORTS_DIR / "velora_test_cases.xlsx"

# Color Palette (Tailwind Slate Theme)
HEADER_BG = "1E293B"       # Slate 800
HEADER_FG = "FFFFFF"       # White
ZEBRA_BG = "F8FAFC"        # Slate 50
BORDER_COLOR = "CBD5E1"    # Slate 300
ACCENT_BLUE = "2563EB"     # Blue 600
CARD_BG = "F1F5F9"         # Slate 100

THIN_BORDER = Border(
    left=Side(style="thin", color=BORDER_COLOR),
    right=Side(style="thin", color=BORDER_COLOR),
    top=Side(style="thin", color=BORDER_COLOR),
    bottom=Side(style="thin", color=BORDER_COLOR),
)

HEADER_FONT = Font(name="Segoe UI", size=11, bold=True, color=HEADER_FG)
HEADER_FILL = PatternFill(start_color=HEADER_BG, end_color=HEADER_BG, fill_type="solid")
HEADER_ALIGNMENT = Alignment(horizontal="center", vertical="center", wrap_text=True)

DATA_FONT = Font(name="Segoe UI", size=10)
DATA_ALIGNMENT_DEFAULT = Alignment(vertical="top", wrap_text=True)
DATA_ALIGNMENT_CENTER = Alignment(horizontal="center", vertical="top")


def parse_markdown_table(file_path: Path) -> Tuple[List[str], List[List[str]]]:
    """Extract headers and rows from markdown tables inside a file."""
    if not file_path.exists():
        return [], []

    content = file_path.read_text(encoding="utf-8")
    lines = [line.strip() for line in content.splitlines()]

    headers: List[str] = []
    rows: List[List[str]] = []
    in_table = False

    for line in lines:
        if not line.startswith("|") or not line.endswith("|"):
            in_table = False
            continue

        cells = [c.strip().replace("`", "") for c in line.split("|")[1:-1]]

        # Skip separator rows like | :--- | :---: |
        if all(re.match(r"^:?-+:?$", c) for c in cells):
            in_table = True
            continue

        if not in_table and not headers:
            headers = cells
            continue

        if in_table and headers:
            # Replace markdown line breaks with real newlines
            clean_cells = [c.replace("<br>", "\n").replace("**", "") for c in cells]
            # Ensure rows only append if first column looks like a TC ID
            if clean_cells and (re.match(r"^[A-Z]{3,4}-\d+", clean_cells[0]) or re.match(r"^VEL-\d+", clean_cells[0])):
                rows.append(clean_cells)

    return headers, rows


def style_table_sheet(sheet: Any, title: str, headers: List[str], rows: List[List[str]]) -> None:
    """Populate and format a worksheet with headers, borders, zebra striping, and auto-filters."""
    sheet.title = title
    sheet.views.sheetView[0].showGridLines = True
    sheet.freeze_panes = "A2"

    # Write Headers
    for col_idx, header in enumerate(headers, start=1):
        cell = sheet.cell(row=1, column=col_idx, value=header)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = HEADER_ALIGNMENT
        cell.border = THIN_BORDER
    sheet.row_dimensions[1].height = 28

    # Write Data Rows
    center_cols = {1, 2, 3, 7, 9}  # ID, Priority, Type, Automation Status, Linked Bug
    for row_idx, row_data in enumerate(rows, start=2):
        is_zebra = (row_idx % 2 == 0)
        row_fill = PatternFill(start_color=ZEBRA_BG, end_color=ZEBRA_BG, fill_type="solid") if is_zebra else None

        for col_idx, value in enumerate(row_data, start=1):
            cell = sheet.cell(row=row_idx, column=col_idx, value=value)
            cell.font = DATA_FONT
            cell.border = THIN_BORDER
            if row_fill:
                cell.fill = row_fill
            cell.alignment = DATA_ALIGNMENT_CENTER if col_idx in center_cols else DATA_ALIGNMENT_DEFAULT

        # Adjust row height based on content newlines
        max_newlines = max((str(val).count("\n") for val in row_data), default=0)
        sheet.row_dimensions[row_idx].height = max(22, (max_newlines + 1) * 16)

    # Auto-adjust column widths
    for col_idx, header in enumerate(headers, start=1):
        col_letter = get_column_letter(col_idx)
        max_len = len(header)
        for row in rows:
            if col_idx - 1 < len(row):
                first_line = str(row[col_idx - 1]).split("\n")[0]
                max_len = max(max_len, min(len(first_line), 55))
        sheet.column_dimensions[col_letter].width = max(max_len + 4, 12)

    # Enable Auto-filters
    if headers and rows:
        last_col = get_column_letter(len(headers))
        sheet.auto_filter.ref = f"A1:{last_col}{len(rows) + 1}"


def create_dashboard_sheet(wb: Any, total_cases: int, module_counts: Dict[str, int]) -> None:
    """Create a high-level summary dashboard with KPI metric cards."""
    ws = wb.create_sheet(title="Dashboard", index=0)
    ws.views.sheetView[0].showGridLines = True

    # Title Banner
    ws.merge_cells("B2:G2")
    title_cell = ws["B2"]
    title_cell.value = "Velora Web App — Test Automation & Case Catalog Dashboard"
    title_cell.font = Font(name="Segoe UI", size=16, bold=True, color="0F172A")
    title_cell.alignment = Alignment(vertical="center")
    ws.row_dimensions[2].height = 36

    # KPI Cards
    kpis = [
        ("Total Test Cases", f'=COUNTA(All_Test_Cases!A2:A{total_cases + 2})', "1E293B"),
        ("P0 (Smoke Tests)", '=COUNTIF(All_Test_Cases!B2:B100, "P0")', "047857"),       # Green
        ("P1 (Core Functional)", '=COUNTIF(All_Test_Cases!B2:B100, "P1")', "B45309"),   # Amber
        ("P2 (Negative / Edge)", '=COUNTIF(All_Test_Cases!B2:B100, "P2")', "4338CA"),   # Indigo
        ("Automated Tests", '=COUNTIF(All_Test_Cases!G2:G100, "*Automated*")', "0284C7"), # Sky
    ]

    for idx, (label, formula, col_hex) in enumerate(kpis):
        col_letter = get_column_letter(idx + 2)
        # Value cell
        v_cell = ws[f"{col_letter}4"]
        v_cell.value = formula
        v_cell.font = Font(name="Segoe UI", size=20, bold=True, color=col_hex)
        v_cell.alignment = Alignment(horizontal="center", vertical="center")
        v_cell.border = THIN_BORDER
        v_cell.fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")

        # Label cell
        l_cell = ws[f"{col_letter}5"]
        l_cell.value = label
        l_cell.font = Font(name="Segoe UI", size=9, bold=True, color="64748B")
        l_cell.alignment = Alignment(horizontal="center", vertical="center")
        l_cell.border = THIN_BORDER
        l_cell.fill = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")

        ws.column_dimensions[col_letter].width = 24
    ws.row_dimensions[4].height = 38
    ws.row_dimensions[5].height = 24

    # Functional Module Breakdown Table
    ws["B7"].value = "Functional Modules"
    ws["B7"].font = Font(name="Segoe UI", size=13, bold=True, color="0F172A")

    headers = ["#", "Functional Area", "Markdown Source File", "Test Suite", "Test Cases"]
    for col_idx, h in enumerate(headers, start=2):
        cell = ws.cell(row=8, column=col_idx, value=h)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = HEADER_ALIGNMENT
        cell.border = THIN_BORDER
    ws.row_dimensions[8].height = 26

    modules_data = [
        ("1", "Authentication & Session", "docs/test_cases/auth_test_cases.md", "tests/auth/test_auth.py", module_counts.get("auth", 0)),
        ("2", "Projects & Workflows", "docs/test_cases/projects_test_cases.md", "tests/projects/test_*.py", module_counts.get("projects", 0)),
        ("3", "Runs & Workflow Lifecycle", "docs/test_cases/runs_and_workflow_test_cases.md", "tests/projects/test_run_workflow.py", module_counts.get("workflow", 0)),
        ("4", "Platform & Settings", "docs/test_cases/platform_and_settings_test_cases.md", "tests/navigation/ & tests/settings/", module_counts.get("platform", 0)),
    ]

    for row_idx, row_values in enumerate(modules_data, start=9):
        is_zebra = (row_idx % 2 == 0)
        row_fill = PatternFill(start_color=ZEBRA_BG, end_color=ZEBRA_BG, fill_type="solid") if is_zebra else None
        for col_idx, val in enumerate(row_values, start=2):
            cell = ws.cell(row=row_idx, column=col_idx, value=val)
            cell.font = DATA_FONT
            cell.border = THIN_BORDER
            if row_fill:
                cell.fill = row_fill
            cell.alignment = Alignment(horizontal="center" if col_idx in (2, 6) else "left", vertical="center")
        ws.row_dimensions[row_idx].height = 24


def export_all() -> Path:
    """Read all functional markdown files and export the consolidated Excel workbook."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    wb = openpyxl.Workbook()
    # Remove default sheet
    default_sheet = wb.active

    files_map = [
        ("auth", "Authentication", DOCS_TC_DIR / "auth_test_cases.md"),
        ("projects", "Projects_and_Workflows", DOCS_TC_DIR / "projects_test_cases.md"),
        ("workflow", "Runs_and_Workflows", DOCS_TC_DIR / "runs_and_workflow_test_cases.md"),
        ("platform", "Platform_and_Settings", DOCS_TC_DIR / "platform_and_settings_test_cases.md"),
    ]

    all_headers: List[str] = []
    all_rows: List[List[str]] = []
    module_counts: Dict[str, int] = {}

    for key, sheet_title, file_path in files_map:
        headers, rows = parse_markdown_table(file_path)
        module_counts[key] = len(rows)
        if not all_headers and headers:
            all_headers = headers
        all_rows.extend(rows)

        # Create individual module worksheet
        ws = wb.create_sheet(title=sheet_title)
        style_table_sheet(ws, sheet_title, headers, rows)

    # Create All_Test_Cases worksheet
    ws_all = wb.create_sheet(title="All_Test_Cases")
    style_table_sheet(ws_all, "All_Test_Cases", all_headers, all_rows)

    # Parse and add defects table if present in auth_test_cases.md
    defect_headers = ["Bug ID", "Severity / Priority", "Status", "Linked Test Cases", "Automation & Verification Notes"]
    defect_rows = [
        ["VEL-025", "Major - S2 / P1 - Blocker", "Pending Fix", "AUTH-12", "UI + Firebase accounts:sendOobCode returns HTTP 200 and loads Step 2, but actual reset email delivery is not received. Verify SMTP delivery."],
        ["VEL-026", "Medium - S3 / P2 - High", "Pending Fix", "AUTH-14, AUTH-15", "Enforces strict email format parsing and OWASP generic enumeration defense notice."],
    ]
    ws_defects = wb.create_sheet(title="Defects_Traceability")
    style_table_sheet(ws_defects, "Defects_Traceability", defect_headers, defect_rows)

    # Create Dashboard at the first position
    create_dashboard_sheet(wb, len(all_rows), module_counts)

    # Remove initial blank sheet
    if default_sheet is not None:
        wb.remove(default_sheet)

    wb.save(OUTPUT_EXCEL)
    print(f"Successfully generated Excel test case catalog: {OUTPUT_EXCEL}")
    print(f"Total Test Cases Exported: {len(all_rows)} across 4 functional modules.")
    return OUTPUT_EXCEL


if __name__ == "__main__":
    export_all()
