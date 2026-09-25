# Synthetic test graph fixtures

Files below were generated programmatically. They do not originate from copyrighted papers or reports.

- `T01-linear.png` — 900×540 pixels, X ticks (96,420)=0 and (770,420)=100; Y ticks (96,420)=0 and (96,85)=50. The midpoint (433,252.5) equals (50,25).
- `T02-reversed.png` — same pixel geometry with X and Y labels reversed. Tests the signed linear conversion even when axes are inverted.
- `T08-transparent.png` — transparent PNG graph background used to inspect overlay alignment.
- `T08-orientation-6.jpg` — JPEG pixels 240×120 with EXIF orientation 6; should display with dimensions 120×240 when loaded via `createImageBitmap`.
- `T08-test.webp` — WebP form of the baseline graph.

`node tests/test-core.mjs` tests the pure conversion and CSV functions directly from the actual HTML source. Actual image decoding, orientation, pointer hit-testing and downloads require browser integration tests (`tests/test-browser.py`).

PDF fixtures for v0.5.0 are generated locally for regression testing:

- `sample-2pages.pdf` — two-page synthetic PDF with graph-like vector content used for page selection and crop/apply tests.
- `protected.pdf` — password-protected synthetic PDF used to verify dedicated password guidance without destroying current work.
- `corrupt.pdf` — intentionally invalid PDF bytes used to verify generic PDF read-error separation.

`python tests/test-v050-browser.py` covers these PDF states plus the mobile touch loupe/nudge/confirm flow.
