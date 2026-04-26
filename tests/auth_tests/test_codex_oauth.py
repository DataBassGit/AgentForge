import sys
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from agentforge.apis.base_api import NonRetriableModelError
from agentforge.auth.codex_oauth import get_codex_credentials


def test_cached_token_success_path(monkeypatch):
    login_mock = MagicMock()
    module = SimpleNamespace(
        get_token=MagicMock(return_value={"access": "token_a", "account_id": "acct_a"}),
        login_oauth_interactive=login_mock,
    )
    monkeypatch.setitem(sys.modules, "oauth_cli_kit", module)

    credentials = get_codex_credentials(interactive=False)

    assert credentials.access_token == "token_a"
    assert credentials.account_id == "acct_a"
    login_mock.assert_not_called()


def test_interactive_login_path_is_invoked(monkeypatch):
    login_mock = MagicMock()
    tokens = [
        None,
        {"access_token": "token_b", "account_id": "acct_b"},
    ]
    module = SimpleNamespace(
        get_token=MagicMock(side_effect=lambda: tokens.pop(0)),
        login_oauth_interactive=login_mock,
    )
    monkeypatch.setitem(sys.modules, "oauth_cli_kit", module)

    credentials = get_codex_credentials(interactive=True)

    assert credentials.access_token == "token_b"
    assert credentials.account_id == "acct_b"
    login_mock.assert_called_once()


def test_non_interactive_missing_token_error_text(monkeypatch):
    module = SimpleNamespace(
        get_token=MagicMock(return_value=None),
        login_oauth_interactive=MagicMock(),
    )
    monkeypatch.setitem(sys.modules, "oauth_cli_kit", module)

    with pytest.raises(NonRetriableModelError, match="python -m agentforge.init_codex_oauth"):
        get_codex_credentials(interactive=False)


def test_force_reauth_ignores_cached_token(monkeypatch):
    login_mock = MagicMock()
    get_token_mock = MagicMock(return_value={"access_token": "fresh_token", "account_id": "acct_c"})
    module = SimpleNamespace(
        get_token=get_token_mock,
        login_oauth_interactive=login_mock,
    )
    monkeypatch.setitem(sys.modules, "oauth_cli_kit", module)

    credentials = get_codex_credentials(interactive=True, force_reauth=True)

    assert credentials.access_token == "fresh_token"
    assert credentials.account_id == "acct_c"
    login_mock.assert_called_once()
    assert get_token_mock.call_count == 1
