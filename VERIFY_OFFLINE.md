# Graph Digitizer — standalone and offline verification

This checklist is intended for an operator using PowerShell 7 and desktop Chrome/Edge. It is not a declaration that every listed device/platform has already passed. Record actual results in `IMPLEMENTATION_STATUS.md`.

1. On Windows, run `./scripts/check-repository.ps1` in PowerShell 7 and resolve all failures without suppressing template checks.
2. Open **both** `dist/index.html` and `dist/index.self-extract.html` directly from disk (`file://`) in Chrome and Edge. Confirm the supplied Graph Digitizer SVG appears both as favicon and top-left brand icon, the self-extract completes, and there are no CSP/script errors.
3. In DevTools, enable Offline after page load. The app must not fetch remote scripts, fonts, images, workers, WASM, models, APIs, analytics, or telemetry. `connect-src 'none'` must remain set.
4. Repeat image input with sample and real PNG, JPEG (including EXIF orientation), and WebP. Verify picker, drag/drop, clipboard paste, corrupt files, wrong types, >20 MiB files, and images >16 million pixels.
5. **PDF offline check:** load a normal multipage PDF (≤80 MiB) while Offline. Switch pages, draw a crop, and use the selected page. Confirm Network shows no CDN/worker/WASM request. Repeat in readable and self-extracting HTML.
6. With an existing calibrated graph and points, open a second PDF, then cancel/close it. Existing work must remain unchanged. Repeat with a corrupt PDF and a password-protected PDF; confirm different error guidance and no loss of current work.
7. While switching PDF pages quickly, verify an older page render cannot appear after a newer choice. Test a visually complex page and confirm a processing/loading state remains visible rather than showing a frozen/blank control state.
8. Calibrate linear/log10 independently for X and Y. Verify 1/10/100 spacing, reversed numerical directions, live recalculation after axis edits, rejection of log values ≤0, too-close markers, and nearly parallel axes. Use a graph rotated by several degrees and confirm known values through affine calibration.
9. Add/drag/nudge manual points; exercise Undo/Redo, zoom/pan/Fit and verify graph values are invariant under viewport changes.
10. Replace an image with unsaved points: cancel and ensure no change; confirm replacement clears prior points/calibration. Test rapid replacement so old images/results/history cannot reappear.
11. Add multiple series, rename/recolor/toggle visibility, place points, guarded-delete a populated series and Undo/Redo. Export standard `series,segment,x,y` CSV and verify UTF-8 BOM, RFC 4180 quoting, grouping/order and optional simple `x,y` output.
12. Auto-trace: pick a curve color, use Axis area, run and inspect the preview **before** applying. Verify review markers/segment gaps, Apply, manual correction, Undo/Redo, and replacement confirmation for a populated series. Repeat with custom trace rectangle and optional start point.
13. During a long/large auto-trace, press Cancel and verify no preview appears later. Alter a trace setting or replace the image while processing; stale results must never appear. Use deliberate gaps/crossings/grid interference/unmatched color to verify uncertain/missing data is visible rather than silently invented.
14. **Mobile touch placement:** on 320/360/390/430px widths and a physical touch device, tap a calibration/manual point. It should remain tentative, with the loupe and nudge controls visible. Nudge by one pixel, Confirm, and verify the committed point moved exactly. Cancel must leave data unchanged.
15. Crop the working image without losing markers/points; confirm excluding any marker/point is rejected. Successful crop clears history and cannot itself be undone. Check Japanese/English, keyboard focus, dialog Escape, help scrolling, toast placement and empty/error states.
16. **Review & repair:** create an auto-traced result with at least one `needsReview` point and at least two segments. On Results, verify the source overlay, redrawn chart, review list, and numeric table select the same point. Mark the review point complete, confirm the “Review next” shortcut disappears at zero, split/merge a segment, then Undo/Redo without leaving Results.
17. **CSV preview:** select all series and one specific series, switch between standard/simple only when valid, verify the preview matches the downloaded UTF-8 BOM CSV, check commas/quotes/newlines in series names, and test Copy plus Select-preview fallback.
18. **Portable project:** create a calibrated log/log graph with multiple series/segments and both manual/auto-traced points, save `.graphdigitizer.json`, close/reopen the app, and restore without the original image/PDF. Verify the working image, calibration, scales, series, segments, points, trace/CSV settings and workflow step. Repeat with a project originating from a PDF page.
19. Try corrupt JSON, a foreign format, an unsupported future `formatVersion`, an oversized project and malformed point/image data. None may replace current work. With unsaved work present, cancel the replacement confirmation and verify nothing changes.
20. Confirm header/body identical gutters at desktop widths and 320/360/390/430px mobile widths, including landscape/short viewports. Check no horizontal scrolling, no overlapping bottom bar, adequate tap targets, and PDF/project controls fitting long filenames/page counts.
21. If published, verify the GitHub Pages/Azure Static Web Apps URL. Initial HTML download is normal; clear Network after loading before testing image, PDF, project save/restore, auto-trace and CSV flows.

Run:

```sh
node tests/test-core.mjs
node tests/test-v020-core.mjs
node tests/test-v030-core.mjs
node tests/test-v040-core.mjs
node tests/test-v060-core.mjs
node tests/test-v070-core.mjs
node tests/test-standalone.mjs
```

With Playwright/Chromium:

```sh
python tests/test-browser.py
python tests/test-v020-browser.py
python tests/test-v030-browser.py
python tests/test-v040-browser.py
python tests/test-v050-browser.py
python tests/test-v060-browser.py
python tests/test-v070-browser.py
python tests/test-v080-browser.py
python tests/test-v082-browser.py
python tests/test-v083-browser.py
python tests/test-v084-browser.py
python tests/test-v085-browser.py
```

The Playwright suites may use `page.set_content()` in managed CI/container environments; they do **not** replace direct `file://` and hosted checks. Perspective-distorted or curved axes remain unsupported.

## v0.8.0追加確認

`python tests/test-v080-browser.py` で大画像・異常画像・長いファイル名・短いスマホ画面・日英ヘルプ・フォーカス復帰・外部通信0件を確認します。

## v0.8.3追加確認

`python tests/test-v082-browser.py` で、結果左ペインがデスクトップ画面高内に収まること、再描画／数値表とCSV本文が詳細として折りたたまれること、選択点の明示的な修正導線、結果画面から同じ修正UIへ入れること、320×568pxで横スクロールがないこと、外部通信0件を確認します。

## v0.8.5追加確認

- 初期画面で入力元が左ペインの4ボタンに集約され、中央に重複ボタンがないこと。
- 画像上の空き場所をドラッグして移動でき、ホイール単独で拡大縮小できること。
- 軸点や手動点の単クリック、既存点ドラッグが上記パン操作と競合しないこと。
- 自動追跡の「マーカー」で、線上の四角・丸マーカー中心だけを抽出できること。
- 共有された月別降水量型の折れ線（12マーカー）で12点を検出できること。

## v1.0.0 公開環境での最終確認

- [ ] Windows PowerShell 7で `./scripts/check-repository.ps1` が成功する。
- [ ] `dist/index.html` を `file://` で開き、画像・PDF・自動追跡・マーカー検出・CSV・作業保存/再開を確認する。
- [ ] `dist/index.self-extract.html` でも同じ操作を `file://` で確認する。
- [ ] Chrome / Edge / Firefox / Safari / Android Chromiumで主要フローを確認する。
- [ ] GitHub Pages / Azure Static Web Apps上で主要フローを確認する。
- [ ] DevToolsのNetworkで、ユーザーファイル・座標値・CSV・作業ファイルの外部送信がないことを確認する。
- [ ] 初期・処理中・成功・失敗の各状態、日英、PC/スマホ表示を確認する。

v1.0.0作成時には、この環境で自動化できるNode/Chromium/standalone/self-extract検証を再実行しています。上記は公開先・実機での運用確認項目です。実施結果は `RELEASE_CHECKLIST.md` に記録してください。
