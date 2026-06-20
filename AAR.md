# After Action Review

Continuous improvement log. Each session ends with a brief review: what went well, what didn't, what to change. This is the POOGI (Process Of Ongoing Improvement) record for this project.

## 2026-06-20 — Initial build: design → script → tests → CI → features → release

**What went well:**
- Incremental build order (design → script → tests → CI → features → edge cases → release) worked cleanly with no major rework
- Using the existing `sanitize` binary rather than rolling a regex kept transliteration correct and reduced scope
- CHANGELOG kept current throughout — no scramble at the end to reconstruct what changed
- End-to-end live test with the real API (draft post + image upload) validated the full pipeline before release
- Edge case review caught 8 real bugs in one pass; all fixed with tests

**What didn't go well:**
- 403 from Medium's API only discovered at live-test time — `api_get` was missing error handling that `api_post` already had; the inconsistency wasn't caught until the dedicated edge case review
- GitHub Actions CI failed on first push due to Go version incompatibility with `sanitize@latest`; needed a second pass to switch to pre-built binaries
- `importlib.util.source_file_loader` API was wrong for Python 3.13 — tests couldn't collect until fixed
- YAML parses bare dates (`2026-06-20`) as `datetime.date` objects, not strings — caught by a test assertion failure

**What we'll do differently:**
- Add error handling to all API functions from the start, not just the first one written
- Run a live API test earlier in the session (before CI) to surface auth/network issues sooner
- Check Go toolchain version constraints before using `go install` in CI workflows
