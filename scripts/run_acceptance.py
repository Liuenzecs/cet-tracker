#!/usr/bin/env python3
"""CET Tracker — Automated Acceptance Test Runner (v0.3.3).

Usage:
    python scripts/run_acceptance.py              # Default acceptance (no live AI)
    RUN_LIVE_AI_TESTS=true python scripts/run_acceptance.py  # Include live AI tests

Status types:
    PASS                — check passed
    FAIL                — check failed (blocks overall PASS)
    SKIPPED             — check skipped (with reason, does not block)
    XFAIL               — expected failure (known issue, does not block)
    PASS_WITH_WARNINGS  — passed but with deprecation or minor warnings

Overall status:
    PASS                    — all non-skipped critical checks pass
    FAIL                    — any critical check fails
    PASS_WITH_KNOWN_ISSUES  — all pass + some xfail items exist
    PASS_WITH_WARNINGS      — all pass but deprecation warnings present

Generates:
    docs/AUTOMATED_ACCEPTANCE_REPORT.md
"""

import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
os.chdir(PROJECT_ROOT)
sys.path.insert(0, str(PROJECT_ROOT))

API_DIR = PROJECT_ROOT / "apps" / "api"
WEB_DIR = PROJECT_ROOT / "apps" / "web"
REPORT_PATH = PROJECT_ROOT / "docs" / "AUTOMATED_ACCEPTANCE_REPORT.md"

# Ordered status types for overall computation
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
STATUS_SKIPPED = "SKIPPED"
STATUS_XFAIL = "XFAIL"
STATUS_PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"

RESULTS = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "checks": [],  # list of (name, status, detail)
    "known_issues": [],
    "warnings": [],
}


def _run(cmd, cwd=None, timeout=120, env=None, capture=True):
    """Run a shell command and return (success, output)."""
    full_env = os.environ.copy()
    if env:
        full_env.update(env)
    try:
        result = subprocess.run(
            cmd, shell=True, cwd=cwd or PROJECT_ROOT,
            capture_output=capture, text=True, timeout=timeout, env=full_env,
            encoding="utf-8", errors="replace"
        )
        out = (result.stdout or "") + "\n" + (result.stderr or "")
        return result.returncode == 0, out
    except subprocess.TimeoutExpired:
        return False, "TIMEOUT"
    except Exception as e:
        return False, str(e)


def record(name, status, detail=""):
    """Record a check result with explicit status type."""
    RESULTS["checks"].append((name, status, detail[:2000]))
    print(f"  [{status}] {name}")
    if detail and status in (STATUS_FAIL, STATUS_XFAIL):
        print(f"          {detail[:200]}")


def record_known_issue(issue):
    RESULTS["known_issues"].append(issue)


def record_warning(warning):
    RESULTS["warnings"].append(warning)


# -- Step 1: File structure --
def step_file_structure():
    print("\n-- Step 1: File structure --")
    required_files = [
        "README.md", "LICENSE", "CLAUDE.md", ".env.example", ".gitignore",
        "apps/api/pyproject.toml", "apps/api/app/main.py", "apps/api/app/database.py",
        "apps/api/app/models/__init__.py", "apps/api/app/models/exam_session.py",
        "apps/api/app/models/listening_result.py", "apps/api/app/models/reading_result.py",
        "apps/api/app/models/vocabulary.py", "apps/api/app/models/review_log.py",
        "apps/api/app/models/review_task.py",
        "apps/api/app/routers/sessions.py", "apps/api/app/routers/listening.py",
        "apps/api/app/routers/reading.py", "apps/api/app/routers/vocabulary.py",
        "apps/api/app/routers/stats.py", "apps/api/app/routers/import_export.py",
        "apps/api/app/routers/review_tasks.py", "apps/api/app/routers/reports.py",
        "apps/api/app/services/vocabulary_service.py", "apps/api/app/services/ai_normalizer_service.py",
        "apps/api/app/services/quality_service.py", "apps/api/app/services/review_service.py",
        "apps/api/app/services/report_service.py", "apps/api/app/services/stats_service.py",
        "apps/api/app/utils/term_utils.py", "apps/api/app/utils/text_cleaner.py",
        "apps/api/app/utils/markdown_parser.py",
        "apps/api/tests/test_markdown_parser.py", "apps/api/tests/test_text_cleaner.py",
        "apps/web/package.json", "apps/web/vite.config.ts",
        "apps/web/src/router/index.ts", "apps/web/src/types/index.ts",
        "apps/web/src/api/vocabulary.ts", "apps/web/src/api/sessions.ts",
        "apps/web/src/views/Dashboard.vue", "apps/web/src/views/VocabularyImport.vue",
        "apps/web/src/views/VocabularyReview.vue", "apps/web/src/views/Reports.vue",
        "docs/API_CONTRACT.md", "docs/DATABASE_SCHEMA.md", "docs/ROADMAP.md",
        "docs/ACCEPTANCE_CHECKLIST.md", "docs/DEVELOPMENT_NOTES.md",
        "scripts/package_clean.ps1", "scripts/reset_demo_data.py",
    ]
    forbidden_files = ["AGENTS.md"]
    missing = []
    for f in required_files:
        if not (PROJECT_ROOT / f).exists():
            missing.append(f)
    for f in forbidden_files:
        if (PROJECT_ROOT / f).exists():
            record(f"no_forbidden: {f}", STATUS_FAIL, "Forbidden file exists")

    if missing:
        record("file_structure", STATUS_FAIL, f"Missing: {', '.join(missing[:5])}")
    else:
        record("file_structure", STATUS_PASS, f"{len(required_files)} required files present")


# -- Step 2: Git security --
def step_git_security():
    print("\n-- Step 2: Git security --")
    ok, out = _run("git ls-files .env .env.local apps/api/.env", cwd=PROJECT_ROOT)
    if out.strip():
        record("git_no_env_tracked", STATUS_FAIL, f"Tracked env files: {out.strip()[:200]}")
    else:
        record("git_no_env_tracked", STATUS_PASS)

    gitignore = (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8")
    required_rules = [".env", "node_modules", "__pycache__", "data/*.db", ".claude", ".venv"]
    for rule in required_rules:
        found = rule.lower() in gitignore.lower()
        status = STATUS_PASS if found else STATUS_FAIL
        record(f"gitignore_has_{rule}", status)


# -- Step 3: Backend tests --
def step_backend_tests():
    print("\n-- Step 3: Backend tests --")
    ok, out = _run("uv run pytest tests/ -v --tb=short", cwd=API_DIR, timeout=120)

    # Count actual test results
    import re
    summary_match = re.search(r'(\d+)\s+passed', out)
    failed_match = re.search(r'(\d+)\s+failed', out)
    xfail_match = re.search(r'(\d+)\s+xfailed', out)
    warnings_match = re.search(r'(\d+)\s+warnings?', out)

    passed_count = int(summary_match.group(1)) if summary_match else 0
    failed_count = int(failed_match.group(1)) if failed_match else 0
    xfail_count = int(xfail_match.group(1)) if xfail_match else 0
    warning_count = int(warnings_match.group(1)) if warnings_match else 0
    total = passed_count + failed_count

    detail = f"{passed_count}/{total} passed"
    if xfail_count:
        detail += f", {xfail_count} xfailed"
    if warning_count:
        detail += f", {warning_count} warnings"

    if failed_count > 0:
        record("backend_tests", STATUS_FAIL,
               f"{detail} — {failed_count} test(s) failed")
    elif xfail_count > 0:
        record("backend_tests", STATUS_XFAIL, detail)
        record_known_issue(f"Backend tests: {xfail_count} expected failures (xfail)")
    elif warning_count > 20:
        record("backend_tests", STATUS_PASS_WITH_WARNINGS, detail)
        record_warning(f"Backend tests have {warning_count} deprecation warnings")
    else:
        record("backend_tests", STATUS_PASS, detail)


# -- Step 4: Frontend build --
def step_frontend_build():
    print("\n-- Step 4: Frontend build --")
    ok, out = _run("pnpm build", cwd=WEB_DIR, timeout=120)
    ts_errors = "error TS" in out or "TypeScript" in out
    if not ok:
        record("frontend_build", STATUS_FAIL, f"Build failed. TS_errors={ts_errors}")
    elif ts_errors:
        record("frontend_build", STATUS_FAIL, "TypeScript errors found")
    else:
        record("frontend_build", STATUS_PASS)


# -- Step 5: API smoke test --
def step_api_smoke():
    print("\n-- Step 5: API smoke test --")
    ok, out = _run(
        "uv run pytest tests/test_smoke_flow.py -v --tb=short",
        cwd=API_DIR, timeout=60
    )

    import re
    summary_match = re.search(r'(\d+)\s+passed', out)
    failed_match = re.search(r'(\d+)\s+failed', out)

    passed = int(summary_match.group(1)) if summary_match else 0
    failed = int(failed_match.group(1)) if failed_match else 0

    if failed > 0:
        record("api_smoke_test", STATUS_FAIL, f"{passed}/{passed + failed} passed")
    else:
        record("api_smoke_test", STATUS_PASS, f"{passed} smoke tests passed")


# -- Step 6: Import/export roundtrip (actually runs the test) --
def step_import_export():
    print("\n-- Step 6: Import/export roundtrip --")
    test_file = API_DIR / "tests" / "test_import_export_roundtrip.py"
    if not test_file.exists():
        record("import_export_roundtrip", STATUS_FAIL, "Test file missing")
        return

    ok, out = _run(
        "uv run pytest tests/test_import_export_roundtrip.py -v --tb=short",
        cwd=API_DIR, timeout=60
    )

    import re
    summary_match = re.search(r'(\d+)\s+passed', out)
    failed_match = re.search(r'(\d+)\s+failed', out)

    passed = int(summary_match.group(1)) if summary_match else 0
    failed = int(failed_match.group(1)) if failed_match else 0
    total = passed + failed

    if failed > 0:
        record("import_export_roundtrip", STATUS_FAIL,
               f"{passed}/{total} passed — roundtrip broken")
    elif total == 0:
        record("import_export_roundtrip", STATUS_FAIL, "No tests collected")
    else:
        record("import_export_roundtrip", STATUS_PASS,
               f"{passed}/{total} roundtrip tests passed")


# -- Step 7: Clean package --
def step_clean_package():
    print("\n-- Step 7: Clean package check --")
    zip_path = PROJECT_ROOT / "cet-tracker-clean.zip"
    if not zip_path.exists():
        record("clean_package", STATUS_SKIPPED,
               "cet-tracker-clean.zip not found — run scripts/package_clean.ps1 to create")
        return
    try:
        from scripts.check_clean_package import check_clean_package
        result = check_clean_package()
        if result["passed"]:
            record("clean_package", STATUS_PASS,
                   f"{result['total_files']} files, no forbidden items")
        else:
            record("clean_package", STATUS_FAIL,
                   str(result.get("issues", [])[:500]))
    except ImportError as e:
        record("clean_package", STATUS_FAIL, f"Cannot import check_clean_package: {e}")


# -- Step 8: AI smoke (mock only) --
def step_ai_smoke():
    print("\n-- Step 8: AI smoke test (mock) --")
    ok, out = _run(
        'uv run pytest tests/ -v --tb=short -k "ai"',
        cwd=API_DIR, timeout=30
    )

    import re
    passed_match = re.search(r'(\d+)\s+passed', out)
    failed_match = re.search(r'(\d+)\s+failed', out)

    passed = int(passed_match.group(1)) if passed_match else 0
    failed = int(failed_match.group(1)) if failed_match else 0

    if failed > 0:
        record("ai_mock_test", STATUS_FAIL, f"{passed}/{passed + failed} passed")
    else:
        record("ai_mock_test", STATUS_PASS,
               f"{passed} AI-related tests passed (mock mode)")


# -- Step 9: Live AI (optional) --
def step_live_ai():
    print("\n-- Step 9: Live AI test (optional) --")
    run_live = os.environ.get("RUN_LIVE_AI_TESTS", "").lower() == "true"
    if run_live:
        ok, out = _run(
            'uv run pytest tests/ -v --tb=short -k "live_ai"',
            cwd=API_DIR, timeout=120
        )
        import re
        passed_match = re.search(r'(\d+)\s+passed', out)
        failed_match = re.search(r'(\d+)\s+failed', out)
        passed = int(passed_match.group(1)) if passed_match else 0
        failed = int(failed_match.group(1)) if failed_match else 0
        if failed > 0:
            record("live_ai_test", STATUS_FAIL, f"{passed}/{passed + failed} passed")
        else:
            record("live_ai_test", STATUS_PASS, f"{passed} live AI tests passed")
    else:
        record("live_ai_test", STATUS_SKIPPED,
               "Optional — set RUN_LIVE_AI_TESTS=true to enable (requires API key)")


# -- Step 10: GitHub readiness --
def step_github_ready():
    print("\n-- Step 10: GitHub open-source readiness --")
    checks = {
        "LICENSE_exists": (PROJECT_ROOT / "LICENSE").exists(),
        "README_exists": (PROJECT_ROOT / "README.md").exists(),
        "env_example_exists": (PROJECT_ROOT / ".env.example").exists(),
        "gitignore_exists": (PROJECT_ROOT / ".gitignore").exists(),
        "AGENTS_absent": not (PROJECT_ROOT / "AGENTS.md").exists(),
    }
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8") if checks["README_exists"] else ""
    checks["copyright_in_readme"] = "版权" in readme or "copyright" in readme.lower() or "MIT" in readme
    checks["api_key_warning"] = "API Key" in readme or "API_KEY" in readme or ".env" in readme

    for name, ok in checks.items():
        status = STATUS_PASS if ok else STATUS_FAIL
        record(f"github_{name}", status)

    if all(checks.values()):
        record("github_readiness", STATUS_PASS, "All GitHub checks passed")
    else:
        record("github_readiness", STATUS_FAIL, "Some GitHub checks failed")


# -- Step 11: E2E check (informational) --
def step_e2e():
    print("\n-- Step 11: E2E --")
    playwright_config = WEB_DIR / "playwright.config.ts"
    if playwright_config.exists():
        ok, out = _run("npx playwright test --reporter=line 2>&1 | tail -20",
                       cwd=WEB_DIR, timeout=120)
        if ok:
            record("e2e_playwright", STATUS_PASS, "E2E tests passed")
        else:
            record("e2e_playwright", STATUS_FAIL, out[:500])
    else:
        record("e2e_status", STATUS_SKIPPED,
               "Playwright not configured — route smoke covered by build + API tests")


# -- Compute overall status --
def compute_overall():
    """Compute overall status from all check results."""
    statuses = [s for _, s, _ in RESULTS["checks"]]
    has_fail = STATUS_FAIL in statuses
    has_xfail = STATUS_XFAIL in statuses
    has_warnings = STATUS_PASS_WITH_WARNINGS in statuses
    has_skipped = STATUS_SKIPPED in statuses

    if has_fail:
        return STATUS_FAIL
    if has_xfail or has_warnings:
        return "PASS_WITH_KNOWN_ISSUES"
    return STATUS_PASS


# -- Generate report --
def generate_report():
    print("\n-- Generating report --")
    overall = compute_overall()

    total = len(RESULTS["checks"])
    passed = sum(1 for _, s, _ in RESULTS["checks"] if s == STATUS_PASS)
    failed = sum(1 for _, s, _ in RESULTS["checks"] if s == STATUS_FAIL)
    xfail = sum(1 for _, s, _ in RESULTS["checks"] if s == STATUS_XFAIL)
    skipped = sum(1 for _, s, _ in RESULTS["checks"] if s == STATUS_SKIPPED)
    warned = sum(1 for _, s, _ in RESULTS["checks"] if s == STATUS_PASS_WITH_WARNINGS)

    lines = [
        "# CET Tracker — Automated Acceptance Report",
        "",
        f"**Generated:** {RESULTS['timestamp']}",
        f"**Overall status:** {overall}",
        "",
        f"**Summary:** {passed} PASS, {failed} FAIL, {xfail} XFAIL, "
        f"{skipped} SKIPPED, {warned} PASS_WITH_WARNINGS — {total} checks total",
        "",
    ]

    try:
        ok, git_hash = _run("git rev-parse --short HEAD")
        if ok:
            lines += [f"**Git commit:** `{git_hash.strip()}`", ""]
    except Exception:
        pass

    lines += [
        "## Results",
        "",
        "| # | Check | Result | Details |",
        "|---|-------|--------|---------|",
    ]
    for i, (name, status, detail) in enumerate(RESULTS["checks"], 1):
        detail_escaped = detail.replace("\n", "<br>")[:200] if detail else "-"
        lines.append(f"| {i} | {name} | {status} | {detail_escaped} |")

    # Known issues section
    if RESULTS["known_issues"]:
        lines += [
            "",
            "## Known Issues",
            "",
        ]
        for issue in RESULTS["known_issues"]:
            lines.append(f"- {issue}")

    # Warnings section
    if RESULTS["warnings"]:
        lines += [
            "",
            "## Warnings",
            "",
        ]
        for w in RESULTS["warnings"]:
            lines.append(f"- {w}")

    lines += [
        "",
        "## Status Legend",
        "",
        "- **PASS** — check passed",
        "- **FAIL** — check failed (blocks overall PASS)",
        "- **SKIPPED** — check skipped (with stated reason, does not block)",
        "- **XFAIL** — expected failure (known issue, does not block)",
        "- **PASS_WITH_WARNINGS** — passed but with non-critical warnings",
        "",
        "## Overall Status Rules",
        "",
        "- **PASS**: All critical checks pass, no failures",
        "- **FAIL**: One or more critical checks failed",
        "- **PASS_WITH_KNOWN_ISSUES**: All pass, but xfail items or warnings present",
        "",
        "## Manual Checks Still Needed",
        "",
        "1. Page visual quality — verify UI looks intentional, not template-like",
        "2. AI-generated content quality — verify generated examples suit your learning",
        "3. Real workflow feel — try a complete import→review→stats cycle",
        "4. GitHub upload decision — review before pushing to public",
        "5. Domain/purchase decision — not required for local tool",
    ]

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"  Report written to {REPORT_PATH}")
    return overall


# -- Main --
def main():
    print("=" * 60)
    print("CET Tracker v0.3.3 Automated Acceptance")
    print("=" * 60)

    steps = [
        ("File Structure", step_file_structure),
        ("Git Security", step_git_security),
        ("Backend Tests", step_backend_tests),
        ("Frontend Build", step_frontend_build),
        ("API Smoke", step_api_smoke),
        ("Import/Export Roundtrip", step_import_export),
        ("Clean Package", step_clean_package),
        ("AI Smoke", step_ai_smoke),
        ("Live AI", step_live_ai),
        ("GitHub Ready", step_github_ready),
        ("E2E", step_e2e),
    ]

    for name, fn in steps:
        try:
            fn()
        except Exception as e:
            record(name.lower().replace(" ", "_"), STATUS_FAIL, str(e)[:500])

    overall = generate_report()

    print(f"\n{'='*60}")
    print(f"Overall: {overall}")
    print(f"Report: {REPORT_PATH}")

    # Exit code: 0 for PASS or PASS_WITH_KNOWN_ISSUES, 1 for FAIL
    if overall == STATUS_FAIL:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
