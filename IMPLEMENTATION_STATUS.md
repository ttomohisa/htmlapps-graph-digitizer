# Graph Digitizer — implementation and verification status

As of 2026-09-26. **Current implementation: v1.0.0 release package (not yet publicly released).** `APP_SPEC.md` records the v1.0.0 product specification and acceptance criteria.

## v1.0.0 preparation status

- **Project owner decision:** prepare v1.0.0 from the v0.9.0 RC, with the marker-delete fix included before the first public release.
- **Feature scope:** unchanged from the RC apart from the final marker-selection/Delete reliability fix; versioning, documentation, screenshots and artifacts are aligned to v1.0.0.
- **Verification disclosure:** automated checks available in this environment pass; target-platform manual checks remain documented in `RELEASE_CHECKLIST.md`.

Automated checks completed in this build environment:

- T01–T13 logic/integration coverage from the existing Node and Chromium suites.
- Readable standalone HTML structure, pinned embedded PDF.js assets, CSP `connect-src 'none'`, no external script/style references, canonical favicon/header icon parity.
- Self-extract gzip payload hash and byte-for-byte restoration to the readable standalone HTML.
- Marker-bearing line chart regression, including preview selection and Delete exclusion before applying points.
- Mobile Chromium layout coverage at 320/360/390/430 px from the existing suites.

Target-environment checks not independently reproducible here:

- Run the unchanged template `./scripts/check-repository.ps1` with PowerShell 7 on Windows.
- Open both standalone variants directly with `file://` on Windows Chrome/Edge and confirm image, PDF, auto-trace, project save/restore, and CSV.
- Verify the deployed GitHub Pages / Azure Static Web Apps build.
- Manual Firefox, Safari/macOS+iOS, and physical Android device checks.
- Confirm browser network logs remain free of file/value uploads in those direct/deployed environments.

These checks are retained as operator verification items in `RELEASE_CHECKLIST.md`; they are not represented as passed by this preparation environment.

## Implemented in v0.1.0–v0.4.0 (retained)

- Browser Kitty template v1.3 structure, shared components, CI/deploy/build scripts, runtime-network blocker, Japanese/English UI, and the user-supplied Graph Digitizer SVG as the identical favicon/top-left brand icon.
- PNG/JPEG/WebP input, guarded replacement, 20 MiB / 16-million-pixel limits, sample graph, four-step workflow, aligned header/body gutters, and responsive desktop/mobile layouts.
- Linear/log10 four-marker calibration with reversed values and a two-dimensional affine transform for mildly rotated straight XY axes; invalid log values, too-short spans and near-parallel axes are rejected.
- Manual point placement/editing, zoom/pan/Fit, drag and keyboard nudge, Undo/Redo, rectangle crop, up to 12 series, visibility/name/color editing, and standard/simple CSV.
- Preview-first color auto-trace with representative-color picking, axis/custom range, optional start point, tolerance/continuity/sampling/gap controls, cancellation/stale-run protection, review markers, separate segments for long gaps, guarded apply, and manual repair.
- Results overlay, redrawn numeric graph, extrapolation warning, and CSV filename/format controls.

## Added in v0.5.0

- **PDF input without runtime upload or CDN:** PDFs up to 80 MiB can be selected or dropped. Opening a PDF creates a staging view and does not overwrite the current graph.
- **Page selection and crop:** page controls render the selected page locally. A rectangle can be selected on the PDF page before converting it into the working image. Existing calibration/points are replaced only after the normal confirmation flow when the staged page is committed.
- **Pinned PDF.js 6.3.289:** `dependencies.json` / `dependencies.lock.json` register the Apache-2.0 dependency. The build embeds `pdf.min.mjs`, `pdf.worker.min.mjs`, `jbig2.wasm`, `openjpeg.wasm`, and `qcms_bg.wasm`; no CDN or external worker is used at runtime.
- **PDF processing states and failure separation:** loading/rendering status is visible; corrupt/unreadable PDFs and password-protected PDFs receive different guidance. Stale page renders are ignored through generation tokens. Cancelling or failing a PDF open leaves current work intact.
- **Mobile guided placement:** on touch input, calibration/manual-extraction taps create a tentative point instead of committing immediately. A magnified pixel view, four 1-pixel nudges, Confirm, and Cancel make the exact point visible outside the finger. Mouse/pen interaction remains direct.
- The existing Image / Axis / Extract / Results fixed mobile tabs remain the primary mobile navigation; bottom-bar spacing continues to protect content from overlap.

## Added in v0.6.0

- **Portable project files:** explicit `.graphdigitizer.json` save/open with format string `browser-kitty.graph-digitizer` and format version 1. The working image is losslessly embedded as PNG together with calibration, linear/log10 scales, series/segments/points, trace settings, CSV settings and workflow step.
- **Resume without the original source:** image-origin projects reopen without the source image; PDF-origin projects reopen from the selected working image and do not embed the original PDF.
- **Validation before replacement:** files over 96 MiB, foreign/corrupt JSON, unsupported future versions, invalid image dimensions/data, malformed calibration/series/points/trace/export settings are rejected before current work is changed.
- **Unsaved-work protection:** project status shows saved/unsaved state, valid project load asks before replacing unsaved work, failed/cancelled loads preserve the current session, and `beforeunload` participates when an image has unsaved edits.
- **Versioned schema:** `schemas/project.schema.json` documents project format v1 using JSON Schema 2020-12. Runtime validation remains the security/compatibility gate before restore.


## Added in v0.7.0

- **Linked review workspace:** the source-image overlay, redrawn graph, review list and numeric table share one selected point. Review-needed points and segment boundaries are listed as concrete repair targets.
- **No meaningless review CTA:** “Review next” is displayed only while `needsReview` points exist; a zero-review result shows the clear state instead. Segment boundaries remain visible independently.
- **Segment repair on Results:** split at the selected point or merge the selected segment into the previous one, with Results-local Undo/Redo and immediate recomputation of chart/table/CSV. The implementation freezes the original segment id before rewriting points to avoid mutation-through-reference bugs.
- **CSV review before download:** choose all series or one series, choose standard/simple format when valid, inspect point/series/segment counts and filename, preview the actual CSV text, copy it or select it as a fallback, then download.
- **Project-format compatibility:** project format version stays at 1; `export.csvTarget` is optional and validated when present, so v0.6 project files remain loadable.


## Carried into v1.0.0 from v0.8.5

- Input sources are consolidated into four left-pane buttons; the central empty preview is drop-only.
- Normal canvas drag pans; mouse wheel zooms without Ctrl. Point dragging and calibration clicks remain distinct from panning.
- Auto-trace has Curve / Markers modes. Marker mode detects local thickness peaks and returns marker centers rather than dense line samples.
- Local color picking estimates the surrounding background and selects the foreground color cluster, improving thin/anti-aliased curve clicks.
- Verified against the supplied monthly-rainfall marker-line image: 12 visible square markers are detected as 12 points with zero runtime network requests.

## Added in v0.8.3

- Replaced the header meta copy with calibration/auto-trace wording while keeping the separate local-processing badge unchanged.
- Aligned the Results clear/review badge with the section title and moved the optional “Review flagged points first” action below the explanatory copy.
- Rebuilt Auto-trace as three consistent setting rows, added an active range-choice state, and made preview actions sequential: Run is hidden once a preview exists, leaving Apply/Discard as the only next decision.

## Automated verification completed in this environment

- `node tests/test-core.mjs`: v0.1 calibration and CSV compatibility.
- `node tests/test-v020-core.mjs`: series/segment sorting, RFC 4180 escaping, UTF-8 BOM, simple-output restrictions and pan/zoom round trips.
- `node tests/test-v030-core.mjs`: color threshold separation, synthetic curve detection, deliberate missing columns, ambiguity and discontinuity handling.
- `node tests/test-v040-core.mjs`: semilog/log-log conversion, positive-log rules, 7-degree affine rotation, inverse mapping, reversed values and near-parallel rejection.
- `node tests/test-v060-core.mjs`: project-format validation for log axes, multiple series/segments, manual+auto points, future-version rejection and malformed records.
- `node tests/test-v070-core.mjs`: RFC 4180 CSV escaping/order, segment-aware simple-format restrictions, and optional target-series project validation.
- `node tests/test-standalone.mjs`: required template paths/markers, `connect-src 'none'`, no external script/style, canonical favicon=brand icon, pinned PDF.js dependency/assets/hashes, and byte-exact gzip self-extract payload.
- `python tests/test-browser.py`: base sample workflow, CSV/language, self-extract, EXIF/replace guard and mobile regression.
- `python tests/test-v020-browser.py`: editing, zoom/pan/Fit, series, CSV, crop, aligned containers, mobile layouts and runtime request/error monitoring.
- `python tests/test-v030-browser.py`: color picking, axis-area auto-trace, cancel/stale prevention, preview-before-apply, apply + Undo/Redo, settings invalidation, optional start point and mobile/network regression.
- `python tests/test-v040-browser.py`: log10 UI, live recalculation, invalid-log guidance, redrawn graph and generated 7-degree rotated-image calibration.
- `python tests/test-v050-browser.py`: real two-page PDF page switch, crop/apply, work preservation until confirmation, corrupt/password-protected PDF separation, zero runtime external requests, touch tentative placement/loupe/nudge/confirm, and mobile horizontal-overflow regression.
- `python tests/test-v060-browser.py`: 339-point log/log two-series manual+auto save/restore, clean/dirty state, cancelled replacement, corrupt/future rejection, zero external project references, and PDF-origin restore without the original PDF on a 390px mobile viewport.
- `python tests/test-v070-browser.py`: linked review selection, zero-review shortcut hiding, segment merge/split + Results Undo, target-series CSV preview/download with special-character names, and 320px mobile review/export overflow.
- `python tests/test-v083-browser.py`: product-specific header copy, unchanged local-processing badge, aligned review badge, consistent auto-trace setting rows, active range choice, sequential preview actions, and 320px overflow regression.
- Retained T05 sample accuracy: default auto-trace reaches **100% X coverage** and **100% of detected points within 2 image pixels of the known curve center** in the bundled synthetic fixture.

## PDF.js standalone details

The generated readable HTML is roughly 1.1 MiB in this preview build; the self-extracting HTML is roughly 1.0 MiB. PDF.js assets are gzip-compressed inside the template dependency bundle and decompressed locally by `StandaloneAssets` when first needed. PDF functionality therefore does not add an external runtime request.

In the managed Chromium test surface used here, a module Worker cannot always start from the in-memory/null-origin page. PDF.js then uses its local same-document fallback and the tested PDF workflow still succeeds with zero external requests. This is not treated as a replacement for the required real hosted/`file://` Worker check.

## Remaining verification / release gates

- **Windows PowerShell 7:** run the unchanged template `./scripts/check-repository.ps1` and official `build-standalone.ps1`, `verify-standalone.ps1`, `verify-self-extract.ps1`.
- **Direct disk / offline:** manually open both generated variants via `file://` in Chrome/Edge with networking disabled and run image **and PDF** workflows. Confirm PDF Worker/Blob/WASM behavior and no CSP error. The managed Chromium environment here blocks `file://` with `ERR_BLOCKED_BY_ADMINISTRATOR`.
- **Hosted environment:** verify the actual GitHub Pages/Azure Static Web Apps page after deployment. This environment also blocks navigation to a local HTTP test server, so hosted module-Worker behavior is still an operator check.
- **Physical devices / additional browsers:** Windows Edge/Chrome, Android Chromium, iOS Safari, macOS/Firefox; in particular verify the touch loupe/nudge flow with real fingers and short/landscape viewports.
- **Real-world PDFs and graphs:** add representative scientific papers/reports (without redistributing copyrighted samples) to manual QA for heavy vector pages, scanned pages, grids/crossings and poor image quality.

## Future milestones

- v0.9.0: release candidate and full regression.
- v1.0.0: General Availability package, including the final marker-selection/Delete fix before the first public release.

### v0.8.0 robustness / accessibility

- Added low-memory large-image guidance and a distinct memory-allocation failure message while preserving current work.
- Added staged PDF resource cleanup and page-hide Worker/Blob cleanup.
- Verified long filenames, corrupt and >16MP images, 320×568 mobile layout, Japanese/English help parity, dialog focus restoration, reduced-motion CSS, keyboard semantics, and zero external runtime requests.
- `tests/test-v080-browser.py` records the new robustness/accessibility regression.

### v0.8.3 interaction / layout polish

- Results keeps the desktop control pane within the viewport; redrawn graph/value table and raw CSV body are collapsed into explicit details sections until needed.
- Extract now exposes a dedicated selected-point repair card. The explicit edit action opens the magnifier/1-pixel nudge flow on desktop and mobile, and Results → Edit on image enters the same flow directly.
- Related commands are grouped under visible labels for input, point operations, segment operations, history, export, and next actions.
- `tests/test-v082-browser.py` verifies compact Results height, the explicit point-repair path, button grouping, 320×568 mobile overflow, and zero external runtime requests.

- `python tests/test-v085-browser.py`: detected marker preview selection, Delete/Backspace exclusion, Undo-safe preview removal, and applying the remaining 11 markers.

## v1.0.0 preparation environment limitations

- `pwsh` / PowerShell 7 is unavailable in this environment, so the official Windows repository check remains pending.
- Direct `file://` navigation was attempted with the managed Chromium executable and was blocked by policy (`ERR_BLOCKED_BY_ADMINISTRATOR`), so direct local-file execution remains a Windows/manual gate.
- The available Chromium regressions use in-memory loading and verify no unexpected HTTP/HTTPS requests for the exercised flows.
