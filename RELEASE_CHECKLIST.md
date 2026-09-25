# Graph Digitizer v1.0.0 release verification record

This record separates checks completed in the available build environment from environment-specific checks that must be performed by an operator on the target platform.

## Automated checks completed for v1.0.0

- [x] T01/T02 calibration and CSV core math
- [x] v0.2 multi-series/segments/zoom coordinate round-trip
- [x] v0.3 curve auto-trace core regression
- [x] v0.4 log10 and rotated-axis calibration
- [x] v0.5 PDF integration regression in managed Chromium
- [x] v0.6 project save/restore regression
- [x] v0.7 linked review/segment repair/CSV preview regression
- [x] v0.8 robustness/accessibility/mobile regression
- [x] direct drag pan and Ctrl-free wheel zoom
- [x] marker-aware extraction on the supplied 12-marker line graph
- [x] marker preview selection + Delete/Backspace exclusion
- [x] readable standalone structure, CSP and embedded dependencies
- [x] self-extract gzip hash + byte-exact restoration
- [x] Japanese/English README and v1.0.0 artifact/version consistency

## Target-environment checks

These checks were not all reproducible inside the managed execution environment used to prepare the release. The project owner authorized preparation of v1.0.0 with these limitations documented rather than represented as passed here.

- [ ] Windows PowerShell 7: `./scripts/check-repository.ps1`
- [ ] Windows Chrome direct `file://`: readable + self-extract
- [ ] Windows Edge direct `file://`: readable + self-extract
- [ ] Firefox manual major-flow check
- [ ] Safari macOS/iOS manual major-flow check
- [ ] Physical Android Chromium manual major-flow check
- [ ] GitHub Pages and/or Azure Static Web Apps deployed check
- [ ] Network log confirms no user-file/value upload in direct/deployed runs

## Environment observations

- PowerShell 7 is not installed in the preparation environment, so the official template PowerShell repository check cannot be executed here.
- Managed Chromium blocks direct `file://` navigation with `ERR_BLOCKED_BY_ADMINISTRATOR`; browser regressions therefore load the standalone app in-memory.
- The available browser regressions record zero unexpected HTTP/HTTPS requests for the exercised flows.

Use `VERIFY_OFFLINE.md` for the full manual procedure.
