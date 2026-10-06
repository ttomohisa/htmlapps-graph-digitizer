Graph Digitizer v1.0.1 — Browser Kitty
===================================

Start with README.ja.md / README.md for usage, build, privacy, limitations, and deployment.
APP_SPEC.md records the v1.0.0 product specification and DEVELOPMENT_PLAN.md records the staged development history.

On Windows with PowerShell 7, run ./scripts/check-repository.ps1, or build using build-standalone.bat.
The source of truth is src/index.template.html; do not hand-edit dist/.

Generated files:
  dist/index.html
  dist/index.self-extract.html

Core checks:
  node tests/test-core.mjs
  node tests/test-v020-core.mjs
  node tests/test-v030-core.mjs
  node tests/test-v040-core.mjs
  node tests/test-v060-core.mjs
  node tests/test-v070-core.mjs
  node tests/test-standalone.mjs

Browser regressions live under tests/test-*-browser.py.
See VERIFY_OFFLINE.md and IMPLEMENTATION_STATUS.md for release verification details and environment-specific checks.
