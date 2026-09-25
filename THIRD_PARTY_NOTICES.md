# Third-Party Notices

Graph Digitizer itself is licensed under MIT. The following runtime component is bundled into the generated standalone HTML for local PDF rendering.

## PDF.js / pdfjs-dist 6.3.289

- Project: PDF.js
- Package: `pdfjs-dist`
- Version: `6.3.289`
- Copyright: Mozilla Foundation and contributors
- License: Apache License 2.0
- Upstream: https://github.com/mozilla/pdf.js
- Bundled form: `legacy/build/pdf.min.mjs`, `legacy/build/pdf.worker.min.mjs`, and the required `jbig2.wasm`, `openjpeg.wasm`, and `qcms_bg.wasm` assets are pinned and embedded by the Browser Kitty standalone build.
- Full license text: `docs/licenses/Apache-2.0-pdfjs.txt`

The dependency version and archive integrity are locked in `dependencies.json` and `dependencies.lock.json`. The generated app does not fetch PDF.js from a CDN at runtime.

The inherited Browser Kitty template build tooling and GitHub Actions retain their respective licenses.
