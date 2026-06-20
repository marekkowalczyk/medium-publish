# Changelog

## [Unreleased]

### Added
- MIT license
- License badge in README
- Note in README that Medium no longer issues new API tokens
- Test article with local images (`test-with-images.md`) confirming end-to-end image upload pipeline

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
