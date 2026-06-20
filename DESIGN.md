# medium-publish — Design Document

## Purpose

A minimal CLI tool + Claude Code skill for publishing Markdown articles to Medium.com
via the Medium REST API. Designed to be called from a Claude Code skill, but usable
standalone from the terminal.

Public repo — intended to be shareable and open-sourced.

---

## Architecture: thin skill over deterministic script

```
owner → /medium-publish skill → medium-publish script → Medium API
```

- **Script** (`medium-publish`): pure mechanics. Takes one argument (`--file`), reads
  YAML frontmatter, validates, calls the API, returns the post URL. No judgment.
- **Skill** (`.claude/skills/medium-publish.md` in `system/`): judgment layer only.
  Resolves ambiguity, confirms before publishing, surfaces validation errors to owner.

All configuration lives in the Markdown file's YAML frontmatter — not in CLI flags.

---

## Script design

### Invocation

```bash
medium-publish --file path/to/article.md
```

Single argument. Everything else comes from frontmatter.

### Frontmatter fields consumed

| Field | Required | Values | Notes |
|---|---|---|---|
| `title` | yes | string | Falls back to H1 if absent (TBD) |
| `medium_status` | yes | `draft` \| `public` \| `unlisted` | Default: `draft` if missing |
| `medium_tags` | no | list, max 5 | Medium enforces the 5-tag limit |
| `medium_canonical_url` | no | URL string | For cross-posts from another platform |
| `medium_publication` | no | publication slug or ID | If absent, posts to personal profile |

### Validation (before any network call)

- `title` present and non-empty
- `medium_status` is one of the three valid values
- `medium_tags` has ≤ 5 entries
- `medium_canonical_url` is a valid URL if present
- API token is available (from `.env` or `MEDIUM_API_TOKEN` env var)
- File exists and is readable

Script exits with a descriptive error on any validation failure. Never hits the
network until all checks pass.

### Auth

Token resolved in this order:
1. `MEDIUM_API_TOKEN` environment variable
2. `.env` file in the repo root (sourced at runtime, gitignored)

`.env.example` is committed and documents the required shape.

### Output

On success: prints the Medium post URL to stdout.
On failure: prints a human-readable error to stderr, exits non-zero.

### Content format

Sends body as `markdown`. The script strips YAML frontmatter before sending —
Medium receives only the body content.

---

## File layout

```
medium-publish/
├── DESIGN.md           ← this file
├── README.md           ← usage, setup, frontmatter reference (write after script works)
├── medium-publish      ← the script (bash or Python, TBD)
├── .env                ← gitignored, holds MEDIUM_API_TOKEN
├── .env.example        ← committed, documents required vars
└── .gitignore
```

---

## Token acquisition

1. Log in to medium.com
2. Go to Settings → Security and apps → Integration tokens
3. Generate a token, copy it
4. Add to `.env`: `MEDIUM_API_TOKEN=your_token_here`

---

## Implementation language decision (open)

**Bash:** minimal dependencies, fast, fits the "thin script" ethos. Requires `curl`
and a YAML parser. Pure-bash YAML parsing is fragile; `yq` is a clean dependency.

**Python:** cleaner YAML parsing (`python-yaml`), better error handling, easier to
test. Heavier than bash but `python3` is always available on macOS.

**Recommendation to resolve in implementation session:** start with Python + `yq`-free
approach using the `python-frontmatter` library. Single file, no build step, shebanged.

---

## Claude Code skill (lives in `system/` repo)

Location: `system/.claude/skills/medium-publish.md`

Responsibility:
- Read the target file's frontmatter
- Surface any missing required fields and ask owner to fill them
- Confirm `medium_status: public` before executing (draft is silent)
- Call `medium-publish --file <path>`
- Report the returned URL to the owner

The skill does NOT write or edit the article. Content is always owner-approved before
the skill is invoked.

---

## What this is NOT

- Not a full Medium API client (no listing posts, editing, analytics)
- Not a bulk publisher
- Not a CMS or content scheduler

If those needs arise, extend; don't over-engineer upfront.

---

## Handoff context (for implementation session)

This design was settled in a `system/` Claude Code session on 2026-06-20. Key decisions:

1. Frontmatter-driven: `--file` is the only CLI argument.
2. Validate everything before hitting the network.
3. Token in `.env` (gitignored) + `MEDIUM_API_TOKEN` env var fallback.
4. Separate public repo (not dotfiles) because: version control isolation, `.env.example`
   as self-documenting contract, potential to grow and be shared.
5. Skill lives in `system/.claude/skills/`, script lives here.
6. Start with Python for cleaner YAML handling.

**First milestone:** working script that can push a draft post. Test with a throwaway
article before wiring the skill.
