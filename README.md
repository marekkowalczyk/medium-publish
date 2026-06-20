# medium-publish

[![Tests](https://github.com/marekkowalczyk/medium-publish/workflows/Tests/badge.svg)](https://github.com/marekkowalczyk/medium-publish/actions)

Publish a Markdown article to Medium from the command line.

```
medium-publish --file path/to/article.md
```

All configuration lives in the article's YAML frontmatter — no flags, no config files. On success, prints the Medium post URL and writes it back into the file's frontmatter to prevent accidental re-publishing.

## Installation

**1. Clone and make the script executable:**

```bash
git clone https://github.com/marekkowalczyk/medium-publish.git
cd medium-publish
chmod +x medium-publish
```

**2. Install Python dependency:**

```bash
pip install python-frontmatter
```

**3. Install [`sanitize`](https://github.com/marekkowalczyk/sanitize)** (used for slug generation):

```bash
go install github.com/marekkowalczyk/sanitize@latest
```

**4. Add your Medium API token:**

```bash
cp .env.example .env
# Edit .env and paste your token
```

Get a token at medium.com → Settings → Security and apps → Integration tokens.

## Usage

### Publish an article

```bash
medium-publish --file my-article.md
```

### Add frontmatter to a new file

```bash
medium-publish --template                        # print to stdout
medium-publish --template --file my-article.md  # prepend to file in place
```

## Frontmatter reference

```yaml
---
title: My Article          # required (falls back to first H1 if absent)
medium_status: draft       # required: draft | public | unlisted
medium_tags: [tag1, tag2]  # optional, max 5
medium_canonical_url:      # optional, for cross-posts
medium_publication:        # optional, publication slug/ID; omit to post to personal profile
slug:                      # optional, overrides filename as slug; both are sanitized
---
```

After publishing, the script writes `medium_url` back into the frontmatter:

```yaml
medium_url: https://medium.com/p/abc123
```

A second run on the same file will error with the existing URL. Remove `medium_url` to republish.

## Auth

Token is resolved in this order:

1. `MEDIUM_API_TOKEN` environment variable
2. `.env` file in the repo root
