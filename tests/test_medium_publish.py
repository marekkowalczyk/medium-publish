"""Tests for medium-publish script."""

import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import frontmatter
import pytest

# Load the script as a module despite having no .py extension
import importlib.machinery
_script = Path(__file__).parent.parent / "medium-publish"
_loader = importlib.machinery.SourceFileLoader("medium_publish", str(_script))
_spec = importlib.util.spec_from_loader("medium_publish", _loader)
_mod = importlib.util.module_from_spec(_spec)
_loader.exec_module(_mod)

sanitize = _mod.sanitize
load_env_file = _mod.load_env_file
validate = _mod.validate
api_get = _mod.api_get
api_post = _mod.api_post
HEADERS_BASE = _mod.HEADERS_BASE
FRONTMATTER_TEMPLATE = _mod.FRONTMATTER_TEMPLATE
SCRIPT = str(_script)


# ---------------------------------------------------------------------------
# sanitize()
# ---------------------------------------------------------------------------

class TestSanitize:
    def test_basic(self):
        assert sanitize("Hello World") == "hello-world"

    def test_special_chars_collapsed(self):
        assert sanitize("My Great Article!") == "my-great-article"

    def test_diacritics(self):
        assert sanitize("café") == "cafe"

    def test_transliteration(self):
        assert sanitize("Łódź") == "lodz"

    def test_already_clean(self):
        assert sanitize("2024-01-31-some-post") == "2024-01-31-some-post"

    def test_no_leading_trailing_hyphens(self):
        result = sanitize("!leading and trailing!")
        assert not result.startswith("-")
        assert not result.endswith("-")


# ---------------------------------------------------------------------------
# load_env_file()
# ---------------------------------------------------------------------------

class TestLoadEnvFile:
    def test_loads_vars(self, tmp_path):
        env = tmp_path / ".env"
        env.write_text("FOO=bar\nBAZ=qux\n")
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("FOO", None)
            os.environ.pop("BAZ", None)
            load_env_file(env)
            assert os.environ["FOO"] == "bar"
            assert os.environ["BAZ"] == "qux"

    def test_does_not_override_existing(self, tmp_path):
        env = tmp_path / ".env"
        env.write_text("FOO=from_file\n")
        with patch.dict(os.environ, {"FOO": "from_env"}):
            load_env_file(env)
            assert os.environ["FOO"] == "from_env"

    def test_ignores_comments_and_blanks(self, tmp_path):
        env = tmp_path / ".env"
        env.write_text("# comment\n\nFOO=bar\n")
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("FOO", None)
            load_env_file(env)
            assert os.environ["FOO"] == "bar"

    def test_missing_file_is_noop(self, tmp_path):
        load_env_file(tmp_path / "nonexistent")  # should not raise


# ---------------------------------------------------------------------------
# validate()
# ---------------------------------------------------------------------------

def make_post(text: str, stem: str = "my-article") -> tuple:
    """Return (post, file_path) for validate()."""
    post = frontmatter.loads(text)
    path = Path(f"/tmp/{stem}.md")
    return post, path


class TestValidate:
    def test_valid_minimal(self):
        post, path = make_post("---\ntitle: Hello\nmedium_status: draft\n---\nBody.")
        params = validate(post, path)
        assert params["title"] == "Hello"
        assert params["status"] == "draft"
        assert params["slug"] == "my-article"

    def test_title_from_h1(self):
        post, path = make_post("---\nmedium_status: draft\n---\n# H1 Title\nBody.")
        params = validate(post, path)
        assert params["title"] == "H1 Title"

    def test_missing_title_raises(self):
        post, path = make_post("---\nmedium_status: draft\n---\nNo heading.")
        with pytest.raises(SystemExit):
            validate(post, path)

    def test_invalid_status_raises(self):
        post, path = make_post("---\ntitle: T\nmedium_status: invalid\n---")
        with pytest.raises(SystemExit):
            validate(post, path)

    def test_too_many_tags_raises(self):
        post, path = make_post("---\ntitle: T\nmedium_status: draft\nmedium_tags: [a,b,c,d,e,f]\n---")
        with pytest.raises(SystemExit):
            validate(post, path)

    def test_five_tags_ok(self):
        post, path = make_post("---\ntitle: T\nmedium_status: draft\nmedium_tags: [a,b,c,d,e]\n---")
        params = validate(post, path)
        assert len(params["tags"]) == 5

    def test_invalid_canonical_url_raises(self):
        post, path = make_post("---\ntitle: T\nmedium_status: draft\nmedium_canonical_url: not-a-url\n---")
        with pytest.raises(SystemExit):
            validate(post, path)

    def test_valid_canonical_url(self):
        post, path = make_post("---\ntitle: T\nmedium_status: draft\nmedium_canonical_url: https://example.com/post\n---")
        params = validate(post, path)
        assert params["canonical_url"] == "https://example.com/post"

    def test_already_published_raises(self):
        post, path = make_post("---\ntitle: T\nmedium_status: draft\nmedium_url: https://medium.com/p/abc\n---")
        with pytest.raises(SystemExit):
            validate(post, path)

    def test_slug_from_filename(self):
        post, path = make_post("---\ntitle: T\nmedium_status: draft\n---", stem="my-great-post")
        params = validate(post, path)
        assert params["slug"] == "my-great-post"

    def test_slug_from_frontmatter_overrides_filename(self):
        post, path = make_post("---\ntitle: T\nmedium_status: draft\nslug: Custom Slug\n---", stem="ignored-name")
        params = validate(post, path)
        assert params["slug"] == "custom-slug"

    def test_multiple_errors_reported(self, capsys):
        post, path = make_post("---\nmedium_status: bad\nmedium_tags: [a,b,c,d,e,f]\n---\nNo title.")
        with pytest.raises(SystemExit):
            validate(post, path)
        err = capsys.readouterr().err
        assert "title" in err
        assert "medium_status" in err
        assert "medium_tags" in err


# ---------------------------------------------------------------------------
# CLI: --template
# ---------------------------------------------------------------------------

class TestTemplateCLI:
    def test_template_stdout(self):
        result = subprocess.run([sys.executable, SCRIPT, "--template"], capture_output=True, text=True)
        assert result.returncode == 0
        assert result.stdout.startswith("---\n")
        assert "medium_status: draft" in result.stdout

    def test_template_prepends_to_file(self, tmp_path):
        article = tmp_path / "article.md"
        article.write_text("# My Article\n\nBody here.\n")
        result = subprocess.run(
            [sys.executable, SCRIPT, "--template", "--file", str(article)],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        content = article.read_text()
        assert content.startswith("---\n")
        assert "# My Article" in content

    def test_template_file_not_found(self, tmp_path):
        result = subprocess.run(
            [sys.executable, SCRIPT, "--template", "--file", str(tmp_path / "ghost.md")],
            capture_output=True, text=True,
        )
        assert result.returncode != 0
        assert "not found" in result.stderr


# ---------------------------------------------------------------------------
# User-Agent header
# ---------------------------------------------------------------------------

def _mock_response(body: dict):
    """Return a mock urllib response for the given JSON body."""
    mock = MagicMock()
    mock.read.return_value = json.dumps(body).encode()
    mock.__enter__ = lambda s: s
    mock.__exit__ = MagicMock(return_value=False)
    return mock


class TestUserAgent:
    def test_api_get_sends_user_agent(self):
        resp = _mock_response({"data": {}})
        with patch("urllib.request.urlopen", return_value=resp) as mock_open:
            api_get("/me", "token123")
            req = mock_open.call_args[0][0]
            # urllib normalises header keys to title-case
            assert "medium-publish" in req.headers["User-agent"]

    def test_api_post_sends_user_agent(self):
        resp = _mock_response({"data": {}})
        with patch("urllib.request.urlopen", return_value=resp) as mock_open:
            api_post("/users/x/posts", "token123", {"title": "T"})
            req = mock_open.call_args[0][0]
            assert "medium-publish" in req.headers["User-agent"]

    def test_user_agent_references_repo(self):
        assert "github.com/marekkowalczyk/medium-publish" in HEADERS_BASE["User-Agent"]
