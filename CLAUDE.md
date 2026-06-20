# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

A minimal CLI tool for publishing Markdown articles to Medium.com via the Medium REST API. Designed to be called from a Claude Code skill (`system/.claude/skills/medium-publish.md`) but also usable standalone.

**Architecture:**
```
owner → /medium-publish skill → medium-publish script → Medium API
```

- **Script** (`medium-publish`): pure mechanics — reads frontmatter, validates, calls the API, prints the post URL. No judgment layer.
- **Skill** (lives in `system/` repo, not here): judgment layer — resolves ambiguity, confirms before publishing public posts, surfaces validation errors.

## Script spec

### Invocation
```bash
medium-publish --file path/to/article.md
```
Single argument. All configuration comes from the file's YAML frontmatter.

### Frontmatter fields
| Field | Required | Notes |
|---|---|---|
| `title` | yes | Falls back to H1 if absent |
| `medium_status` | yes | `draft` \| `public` \| `unlisted`; default `draft` |
| `medium_tags` | no | List, max 5 (Medium-enforced) |
| `medium_canonical_url` | no | Valid URL; for cross-posts |
| `medium_publication` | no | Publication slug/ID; absent = personal profile |
| `slug` | no | Overrides filename as slug source; both sanitized via `sanitize` |

### Validation (must all pass before any network call)
- `title` present and non-empty
- `medium_status` is one of the three valid values
- `medium_tags` has ≤ 5 entries
- `medium_canonical_url` is a valid URL if present
- `MEDIUM_API_TOKEN` available (env var or `.env` file)
- File exists and is readable

### Auth token resolution order
1. `MEDIUM_API_TOKEN` environment variable
2. `.env` file in repo root (gitignored)

`.env.example` is committed as the self-documenting contract for required vars.

### Content handling
Strip YAML frontmatter before sending. Medium receives body only, as `markdown` format.

### Output
- Success: post URL to stdout
- Failure: human-readable error to stderr, exit non-zero

## Dependencies

- **`python-frontmatter`** — YAML frontmatter parsing (`pip install python-frontmatter`)
- **`sanitize`** — slug generation; install from `marekkowalczyk/sanitize` (binary must be on `$PATH`)

Slug defaults to the sanitized filename stem; frontmatter `slug` field overrides it.

## Environment setup

```bash
cp .env.example .env
# Add your token: Settings → Security and apps → Integration tokens on medium.com
```
