# CET Tracker — Automated Acceptance Guide

## Quick Start

```bash
# Full automated acceptance (no live AI calls)
python scripts/run_acceptance.py

# Include live DeepSeek test (requires API key)
# Windows PowerShell:
$env:RUN_LIVE_AI_TESTS="true"
python scripts/run_acceptance.py

# macOS/Linux:
RUN_LIVE_AI_TESTS=true python scripts/run_acceptance.py
```

## What it checks

1. **File structure** — all required source files present, no forbidden files
2. **Git security** — `.env` not tracked, `.gitignore` has required exclusions
3. **Backend tests** — runs `pytest tests/` in `apps/api/` (128 tests expected)
4. **Frontend build** — runs `pnpm build` in `apps/web/`
5. **API smoke test** — creates sessions, entries, reviews, tasks, reports
6. **Import/export roundtrip** — actually runs `test_import_export_roundtrip.py` (create → export → import → verify)
7. **Clean package check** — scans `cet-tracker-clean.zip` for forbidden files
8. **AI smoke test** — mock-only tests for AI endpoints (12 tests)
9. **Live AI test** — optional, requires `RUN_LIVE_AI_TESTS=true`
10. **GitHub readiness** — LICENSE, README, .gitignore, no AGENTS.md
11. **E2E route smoke** — Playwright check (SKIPPED if not configured)

## Status Types

Each check is assigned one of:

| Status | Meaning | Blocks overall PASS? |
|--------|---------|---------------------|
| **PASS** | Check passed | No |
| **FAIL** | Check failed | **Yes** |
| **SKIPPED** | Check skipped with reason | No |
| **XFAIL** | Expected failure (known issue) | No |
| **PASS_WITH_WARNINGS** | Passed with non-critical warnings | No |

## Overall Status Rules

- **PASS**: All critical checks pass, no failures
- **FAIL**: One or more critical checks failed
- **PASS_WITH_KNOWN_ISSUES**: All pass, but xfail items or warnings present

Key rule: **120/123 is never PASS.** If any test fails, backend_tests is FAIL and overall is FAIL.

The script exits with code 0 for PASS or PASS_WITH_KNOWN_ISSUES, code 1 for FAIL.

## Output

Generates `docs/AUTOMATED_ACCEPTANCE_REPORT.md` with:
- Timestamp and git commit hash
- Overall status with explicit status type
- Per-check pass/fail/skip/xfail status with details
- Known issues and warnings sections
- Status legend and overall status rules
- Manual checks still needed

## Manual checks still needed

1. Page visual quality — does the UI feel designed?
2. AI content quality — are generated examples suitable?
3. Real workflow — does `import → review → stats` feel smooth?
4. GitHub upload — review before pushing to public
5. Domain/purchase — not required for local use
