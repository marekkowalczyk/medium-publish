# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

A minimal CLI tool for publishing Markdown articles to Medium.com via the Medium REST API. Designed to be called from a Claude Code skill (`system/.claude/skills/medium-publish.md`) but also usable standalone.

**Architecture:**
```
owner → /medium-publish skill → medium-publish script → Medium API
```

- **Script** (`medium-publish`): pure mechanics — reads frontmatter, validates, uploads local images, calls the API, prints the post URL. No judgment layer.
- **Skill** (lives in `system/` repo, not here): judgment layer — resolves ambiguity, confirms before publishing public posts, surfaces validation errors.

## Commands

```bash
python3 -m pytest tests/ -v   # run tests
make install                   # symlink script to /usr/local/bin
make install INSTALL_DIR=~/bin # custom install location
```

## Script spec

### Invocation
```bash
medium-publish --file path/to/article.md  # publish
medium-publish --template                  # print frontmatter template to stdout
medium-publish --template --file art.md   # prepend/merge template into file
medium-publish --version                   # print version
```

### Frontmatter fields
| Field | Required | Notes |
|---|---|---|
| `title` | yes | Falls back to H1 if absent |
| `medium_status` | yes | `draft` \| `public` \| `unlisted`; default `draft` |
| `medium_tags` | no | List, max 5; duplicates removed with a warning |
| `medium_canonical_url` | no | Valid URL; for cross-posts |
| `medium_publication` | no | Publication slug/ID; absent = personal profile |
| `slug` | no | Overrides filename as slug source; both sanitized via `sanitize` |
| `medium_url` | written on publish | Set automatically after publish; blocks re-publishing |

### Validation (all must pass before any network call)
- `title` present and non-empty (or H1 fallback)
- `medium_status` is one of the three valid values
- `medium_tags` has ≤ 5 entries (after deduplication)
- `medium_canonical_url` is a valid URL if present
- `MEDIUM_API_TOKEN` available (env var or `.env` file)
- `medium_url` not already set (double-publish guard)
- File exists and is readable

### Image handling
Local image paths in the article body (`![alt](./image.png)`) are uploaded to Medium's `/images` endpoint and rewritten to Medium CDN URLs before publishing. Remote URLs pass through unchanged. Images inside fenced code blocks and inline code are skipped. The same image referenced multiple times is uploaded only once.

### Auth token resolution order
1. `MEDIUM_API_TOKEN` environment variable
2. `.env` file in repo root (gitignored)

`.env.example` is committed as the self-documenting contract for required vars.

### Output
- Success: post URL to stdout; `medium_url` written back to the article's frontmatter
- Failure: human-readable error to stderr, exit non-zero

## Dependencies

- **`python-frontmatter`** — YAML frontmatter parsing (`pip install -r requirements.txt`)
- **`sanitize`** — slug generation; install from `marekkowalczyk/sanitize` (binary must be on `$PATH`)

## Environment setup

```bash
cp .env.example .env
# Add your token: Settings → Security and apps → Integration tokens on medium.com
```
