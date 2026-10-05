# Changelog

## Unreleased

- Added exact fractional image X/Y editing to the selected-point loupe, with per-field bounds/errors and atomic Apply/Cancel. Invalid and obsolete drafts cannot change point data; identity, calibration, project format, dependencies, and CSV/TSV behavior stay unchanged.
- Fixed cancelled/return-to-start dragging and clamped keyboard nudges silently changing automatic/review metadata or consuming Undo/Redo. Only real movement marks a point manual/reviewed and creates one history entry.
- Made the repair summary's point number agree with the sorted Results table, including multiple series, segments, and equal-X points.
- Added source/controller regression tests plus tracked-download/readable/self-extract parity checks. Native pointer capture, loupe rendering, mobile layout/keyboard, and visual selection still require browser/device verification for this change.

- Added a separate Japanese/English “Copy for spreadsheet” action using selected-series/format TSV, without changing CSV or project files.
- Spreadsheet-only text-cell normalization prevents tab/newline row splitting and protects formula-like or quote-leading series names; numeric values remain untouched.
- Clipboard rejection or absence opens a selectable full-text fallback, including data beyond the truncated CSV preview; stale asynchronous results are ignored.


Changes to Graph Digitizer follow [Semantic Versioning](https://semver.org/).

## 1.0.0 - 2026-09-26

### Planned General Availability
- Prepared the v0.9.0 release candidate as the first stable v1.0.0 package without adding new end-user feature scope beyond the final marker-selection/Delete reliability fix.
- Fixed marker-preview selection so detected markers are selected on pointer down instead of competing with image panning.
- `Delete` / `Backspace` removes the selected detected marker before applying the preview.
- `Delete` / `Backspace` also removes a selected extracted point in Extract or Results.
- Added an always-visible hint below marker preview results describing click-to-select and Delete-to-remove.
- Unified the app header, `app.config.json`, generated standalone artifacts, README files, screenshots, and release documentation on v1.0.0.
- Rewrote the English/Japanese README files to follow the established Browser Kitty PDF Organizer repository structure: demo, features, quick start, usage, Pages deployment, development/build, privacy, limitations, dependencies, contribution, and license.
- Retained marker-aware tracing, direct drag pan, Ctrl-free wheel zoom, PDF input, project save/restore, linked review, and CSV preview/export behavior.
- Re-ran the available core, standalone/self-extract, and managed-Chromium regression suites against the v1.0.0 artifacts.

**Environment note:** Windows PowerShell 7, direct `file://`, hosted deployment, Safari/Firefox, and physical-device checks cannot all be reproduced in this execution environment. They remain documented in `VERIFY_OFFLINE.md` / `RELEASE_CHECKLIST.md`.

## 0.9.0 - 2026-09-26

### Release Candidate
- Feature freeze: no new end-user feature is introduced after v0.8.5.
- Re-ran the accumulated calibration, CSV, auto-trace, log/rotated-axis, PDF, project, review/export, accessibility, input, marker-detection, and marker-deletion regression suites.
- Refreshed the release-candidate documentation and screenshots against the current UI.
- Revalidated the readable standalone and self-extract structures, CSP/network restrictions, embedded PDF.js dependency metadata, favicon/header icon parity, and self-extract byte restoration.
- Remaining v1.0 gates are Windows PowerShell 7 repository verification, direct `file://`, deployed-host, Firefox/Safari, and physical-device checks.

## 0.8.5 - 2026-09-25

- Marker auto-trace previews can now be selected directly on the graph image.
- Press Delete or Backspace to exclude the selected detected marker before applying the trace result.
- The selected preview marker is visibly highlighted, and removal offers Undo.

## v0.8.4

- 入力画面を整理し、左ペインの4つの入力元（画像 / PDF / 作業ファイル / サンプル）へ集約。中央の空状態はドラッグ＆ドロップ専用にして重複ボタンを削除。
- 画像操作を「ドラッグで移動 / ホイールで拡大縮小」へ変更し、専用の移動ボタンを廃止。
- 自動追跡に「曲線 / マーカー」検出を追加。四角・丸など線より太いマーカー中心だけを抽出できるようにした。
- 色選択を背景推定付きの近傍サンプリングへ変更し、細い線やアンチエイリアス境界で背景色を拾いにくくした。
- マーカー付き折れ線の回帰 fixture を追加し、12個のマーカーを12点として抽出できることを確認。

## v0.8.3

- Replaced the header meta copy “Fully local processing” with a product-specific calibration/auto-trace description while keeping the separate local-processing badge unchanged.
- Fixed the Results “No flagged points” badge alignment by placing the title and badge on one baseline and the explanatory text below them.
- Reworked Auto-trace into three cohesive setting rows (curve color, trace range, optional start point), added an active range choice state, and made the execute/apply flow single-purpose instead of showing Run and Apply at the same time.
- Kept all existing IDs and underlying tracing behavior so v0.8.2 workflows and regressions remain compatible.

## v0.8.2

- Shortened the desktop Results control pane by capping it to the viewport and moving the redrawn graph/value table and raw CSV preview into explicit details sections.
- Added a dedicated manual-point repair card. Selecting a point now exposes a clear **Edit selected point** action with the existing magnifier and 1-pixel nudge UI; Results → **Edit on image** opens the same repair flow directly.
- Reorganized buttons into labeled action groups for input, point editing, edit history, segment operations, export, and next actions so unrelated commands no longer appear in one flat row.
- Kept direct point dragging, keyboard nudging, auto-trace, PDF, projects, CSV formats, and Undo/Redo behavior unchanged.
- Added v0.8.2 browser regression for compact Results height, grouped controls, explicit point repair, 320×568 mobile overflow, and zero external runtime requests.

## v0.8.1

- Unified zoom-out / percentage / zoom-in into one segmented control.
- Clicking the percentage resets the preview to 100%.
- Moved Fit to the right of the zoom control and changed it to an icon button.

## [0.8.0] - 2026-09-24

Hardened large/invalid input handling, mobile/long-text layout, accessibility behavior, and user-facing scope/privacy guidance without changing the v0.7 review workflow.

- Added actionable low-memory guidance for large images (8MP+) on devices reporting 4 GiB or less, while retaining the existing 20 MiB / 16MP hard limits. Image decode/allocation failures now distinguish likely memory exhaustion and preserve current work.
- Strengthened resource cleanup by destroying staged PDF loading/document objects and clearing page canvases when the PDF stage closes; the embedded PDF Worker/Blob URL is terminated/revoked on page hide.
- Added long-string wrapping guards for status/meta/help text and verified short 320×568 mobile layouts and zoomed content without fixed-bar overlap or horizontal overflow.
- Kept/verified reduced-motion behavior, focus-visible styling, dialog focus restoration, aria-live status regions, canvas/result keyboard labels, point arrow-key nudging, and Results keyboard selection.
- Expanded Japanese/English help to state supported XY/log/rotated-axis workflows, unsupported bar/polar/perspective/password-PDF cases, local runtime processing, and the uncertainty of image-derived values.
- Added v0.8 browser regression covering long filenames, large-image/low-memory advice, >16MP rejection, corrupt-image rejection, current-work preservation, Japanese/English help parity, focus restoration, short mobile layout, and zero external runtime requests.

**Release-gate note:** Windows PowerShell 7, direct `file://`, hosted, Safari/Firefox, and physical-device checks remain operator verification items for v0.9.0 RC.

## [0.7.0] - 2026-09-24

Finished the review-and-export workflow so questionable auto-trace output can be inspected, repaired, and verified before CSV download.

- Added a Results review panel with counts for points, series, review-needed points, and segments. Review-needed points and segment boundaries are listed separately; the “Review next” shortcut is hidden when there are zero review-needed points.
- Linked selection across the source-image overlay, redrawn numeric chart, review list, and coordinate table. Selected points remain visible while moving between Results and Extract.
- Added explicit “mark reviewed”, “edit on image”, segment split, and previous-segment merge actions. Fixed segment split/merge to freeze the original segment id before mutation so a selected-point reference cannot partially rewrite a segment.
- Added Undo/Redo directly on Results so review repairs can be reversed without leaving the page. Existing Extract Undo/Redo remains available.
- Added CSV target-series selection, standard/simple format validation, filename/point/series/segment metadata, a readable CSV preview, select-all, and clipboard copy with a selectable-text fallback.
- Preserved RFC 4180 quoting for commas, quotes, and newlines in series names; standard output remains `series,segment,x,y`, while simple `x,y` is offered only for one selected series with one segment.
- Extended project format v1 compatibly with optional `export.csvTarget`; older v1 project files without the field remain valid.
- Added v0.7 core/browser regressions for zero-review CTA hiding, linked selection, segment merge/split + Undo, special-character CSV preview/download, targeted simple CSV, and 320px mobile overflow.

**Release-gate note:** Windows PowerShell 7, direct `file://`, hosted, Safari/Firefox, and physical-device checks remain operator verification items before formal v1.0.0 release.

## [0.6.0] - 2026-09-24

Added explicit portable project save/restore so long digitizing sessions can resume without the original source file.

- Added versioned `.graphdigitizer.json` project files (`formatVersion: 1`) containing the current working image, four calibration markers, axis values/scales, series metadata, segments, extracted points, trace configuration, CSV settings, and workflow step.
- Re-encode the current working image losslessly as embedded PNG. Projects created from a PDF page contain the selected working image only; the original PDF is not copied into the project.
- Added project Save/Open actions to the Image workflow and additional save actions on Extract/Results. Unsaved/saved status is visible, and closing the page with unsaved work participates in the browser before-unload warning.
- Added strict project validation before current work is touched: 96 MiB file limit, format/version/type/range/image-dimension/series/point/trace/export checks, unsupported-future-version handling, and corrupt/decode failure separation.
- Opening a valid project asks before replacing unsaved current work. Cancelling or failing validation leaves the current image/calibration/points unchanged.
- Project restore rebuilds the image, calibration, log/linear scales, multiple series/segments, manual/auto points, trace settings, CSV controls, and workflow step without requiring the original image/PDF or network access.
- Added JSON Schema 2020-12 documentation for project format v1 plus core/browser regression tests. The browser suite verifies a 339-point log/log, two-series manual+auto project round trip and a PDF-origin project resumed without the original PDF.

**Release-gate note:** project save/restore is covered in managed Chromium, but Windows PowerShell 7, direct `file://`, hosted, Safari/Firefox and physical-device checks remain operator verification items before formal v1.0.0 release.

## [0.5.0] - 2026-09-24

Added local PDF input and a mobile-first precision workflow while retaining the v0.4.0 scientific-axis and preview-first auto-trace behavior.

- Added PDF input with an 80 MiB guard, page selection, page-by-page raster rendering, optional rectangle crop, and guarded conversion of the selected page into the working image. Merely opening a PDF does not replace the current graph; replacement occurs only after explicit confirmation.
- Added dedicated error states for corrupt/unreadable PDFs and password-protected PDFs. Page/render generation tokens prevent stale page output from replacing a newer selection.
- Pinned **pdfjs-dist 6.3.289** in the template dependency manifest and lock file. PDF.js core, worker, JPEG 2000/JBIG2/color-management WASM are compressed and embedded into both single-file HTML variants; runtime CDN/remote-worker fallback is not used.
- Added PDF loading/rendering progress and kept the current image/calibration/points intact when a PDF is cancelled or fails to open.
- Kept the existing four-step mobile navigation and added touch-specific tentative point placement: a magnified pixel preview, four 1-pixel nudge buttons, explicit Confirm, and Cancel. Touch placement is used for calibration points and manual extraction while mouse/pen behavior remains direct.
- Added v0.5 Chromium coverage using real two-page, corrupt, and password-protected PDF fixtures. Tests cover page switching, crop/apply, work preservation, zero external runtime requests, touch loupe/nudge/confirm, and mobile horizontal-overflow regression.
- Updated README, offline checklist, implementation status, third-party notices, and bundled Apache-2.0 license text.

**Release-gate note:** the managed Chromium environment used here blocks direct `file://` navigation and local-host navigation, so Windows PowerShell 7, real `file://` PDF Worker/Blob behavior, and physical-device checks remain operator verification items before formal v1.0.0 release. The in-memory Chromium PDF workflow works without external network access; a main-thread PDF.js fallback is available when a module Worker cannot start.

## [0.4.0] - 2026-09-24

Added scientific-axis calibration while retaining the v0.3.0 manual editing and preview-first auto-trace workflow.

- Added independent **linear / log10** scale selection for X and Y. log10 calibration rejects zero, negative, non-finite and duplicate values.
- Replaced separate horizontal-X / vertical-Y conversion with a shared two-dimensional affine calibration derived from the two straight axis lines. Slightly rotated graphs now convert through the same code path as unrotated graphs.
- Added numerical stability checks for too-short calibration spans and nearly parallel X/Y axis lines instead of returning unstable values.
- Axis value or scale edits keep every extracted point at the same image pixel coordinates and recompute numerical X/Y values immediately.
- Updated the calibrated trace-area calculation so a rotated calibration rectangle is converted back to image coordinates before deriving the trace bounds.
- Added a redrawn numerical graph on Results that respects linear/log10 scales, plus warnings when extracted points lie outside the calibrated tick ranges and therefore use extrapolation.
- Added T03/T04 exact-source tests for semilog/log-log values, 7-degree rotation, inverse data↔image mapping, reversed numerical directions and near-parallel rejection. Added Chromium integration coverage for live log recalculation and interactive rotated-axis calibration.

**Scope limits:** perspective correction, curved axes, direct PDF input and portable project save/restore are still outside v0.4.0. Auto-trace remains X-column based and requires review on rotated/noisy graphs. Native Windows PowerShell, direct `file://` and physical-device checks remain separate release gates.

## [0.3.0] - 2026-09-24

Added preview-first, color-based curve auto-tracing while retaining the v0.2.0 precision-editing workflow and Browser Kitty template v1.3 structure.

- Replaced the app favicon and top-left brand icon with the user-supplied optimized Graph Digitizer SVG, using the same canonical asset for both.
- Added representative-color picking from the source image, calibrated-axis/custom trace ranges and an optional preferred start point.
- Added configurable color tolerance, continuity limit, X sampling interval and short-gap handling.
- Added color-run detection and continuity tracking without AI or network APIs. Large jumps are rejected; long missing runs stay as separate segments instead of being silently interpolated.
- Added preview-before-apply with visual review markers, segment gaps, summary counts and confirmation before replacing a populated series. Applied results remain manually editable and Undo/Redo can restore the previous series.
- Added asynchronous progress/cancel behavior plus generation/run-token checks so cancelled or stale traces cannot later overwrite current work.
- Added v0.3 source/browser tests covering missing/ambiguous candidates, discontinuities, cancellation, stale-preview invalidation, optional start points, mobile layout and runtime-network monitoring. The bundled synthetic sample reaches 100% X coverage and 100% of detected points within 2 image pixels at the default settings.

**Scope limits:** automatic tracing still requires user review and is optimized for clearly colored, approximately single-valued XY curves. Log/rotated axes, direct PDF input and portable project save/restore remain future milestones. Native Windows PowerShell, direct `file://` and physical-device checks remain separate release gates.

## [0.2.0] - 2026-09-24

Added precision editing and multiple data series on top of v0.1.0, retaining the Browser Kitty template v1.3 structure and unmodified PowerShell build/check scripts.

- Aligned header and content left/right edges on desktop and mobile.
- Added zoom out/in, Fit, pan mode and Ctrl+wheel zoom with coordinate-preserving canvas overlays.
- Added drag-to-move existing points, keyboard nudges and Undo/Redo for points, series and calibration edits.
- Added up to 12 series with selection, editable names/colors, visibility toggle and guarded deletion.
- Added segment-aware point records and standard `series,segment,x,y` CSV; single-series `x,y` remains available by selection. Escaping uses RFC 4180 for series names.
- Added rectangle crop; only applies when every existing calibration marker and picked point is preserved. Cropping is explicitly non-undoable.
- Added exact-source v0.2 CSV/viewport math tests, Chromium interaction tests and updated screenshots/documentation.

**Scope limits:** auto-trace, log/rotated axes, PDF and portable project save/restore remain future milestones. Native Windows PowerShell `check-repository.ps1`, direct `file://` and physical-device checks are separate release gates.

## [0.1.0] - 2026-09-24

Initial manual XY graph digitization milestone built from the supplied Browser Kitty `htmlapps-template` v1.3.

- Added browser-local PNG/JPEG/WebP import, drag-and-drop, clipboard paste, guarded image replacement, and a generated example graph.
- Added four-point horizontal/vertical linear axis calibration with input and near-degenerate/tilt validation.
- Added single-series manual point selection and insertion, selected-point deletion and Undo, keyboard nudging, point table, and X-sorted `x,y` CSV download (UTF-8 BOM).
- Added Japanese/English interface, responsive desktop layout and four-step mobile tabs, shared template confirmation/toast components, SVG branding, and input/error/empty/result states.
- Kept the template PowerShell build, runtime network blocker, canonical icon embedding, and gzip self-extract mode; added exact-source math/CSV tests and browser smoke fixtures.

**Known scope limits:** no logarithmic axes, auto-trace, direct PDF import, zoom/pan, multiple series, or portable project save/restore yet. See `DEVELOPMENT_PLAN.md` for planned milestones and `IMPLEMENTATION_STATUS.md` for remaining checks.
