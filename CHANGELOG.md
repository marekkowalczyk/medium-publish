# Changelog

## [Unreleased]

## [1.3.0] — 2026-06-20

### Added
- MIT license
- License badge in README
- Note in README that Medium no longer issues new API tokens
- `requirements.txt` for `pip install -r requirements.txt`
- `Makefile` with `make install` target — symlinks script to `/usr/local/bin` (overridable via `INSTALL_DIR`)

### Removed
- Test articles and images (`test-article.md`, `test-with-images.md`, `test-images/`)

## [1.2.0] — 2026-06-20

### Fixed
- Image syntax inside fenced code blocks and inline code no longer triggers uploads
- `api_get` now catches `HTTPError` and `URLError` and exits cleanly; `api_post` and `upload_image` share a common `_api_error()` helper; network errors in all three paths produce a clean error instead of a traceback
- `--template --file` on a file with an empty frontmatter block (`---\n---`) now merges correctly instead of prepending a second block
- Same local image referenced multiple times is uploaded only once
- `sanitize()` now guards against empty input and empty output with a clear error message
- Frontmatter `medium_url` write-back failure after a successful publish is now a warning rather than a crash
- Duplicate entries in `medium_tags` are deduplicated with a stderr warning before the ≤5 check
- Empty article body now emits a stderr warning

## [1.1.0] — 2026-06-20

### Added
- Local images in the article body are uploaded to Medium automatically and rewritten to Medium-hosted URLs before publishing; remote URLs are left as-is
- `--version` flag

## [1.0.0] — 2026-06-20

### Added
- `medium-publish` Python script: publishes a Markdown article to Medium via the REST API
- Frontmatter-driven configuration — `--file` is the only CLI argument
- Validation of all fields before any network call, with all errors reported at once
- `title` falls back to the first H1 heading if not set in frontmatter
- `medium_url` written back to the file's frontmatter after a successful publish; subsequent runs are blocked with the existing URL shown
- `--template` flag: prints canonical YAML frontmatter to stdout
- `--template --file <path>`: prepends the frontmatter block to the file in place
- Slug derived from the filename stem; `slug` frontmatter field overrides it
- Slug sanitization via [`marekkowalczyk/sanitize`](https://github.com/marekkowalczyk/sanitize), handling transliteration (Łódź→lodz, café→cafe, etc.)
- Publication support: `medium_publication` field posts to a named publication; absent posts to personal profile
- Auth via `MEDIUM_API_TOKEN` env var or `.env` file in the repo root
- pytest test suite (39 tests) covering validation, sanitize, env loading, CLI behaviour, User-Agent headers, and image upload
- GitHub Actions CI workflow running tests on every push
- README, CLAUDE.md, DESIGN.md

### Fixed
- 403 Forbidden from Medium API: added a named `User-Agent` header to all requests (`urllib`'s default is blocked)
