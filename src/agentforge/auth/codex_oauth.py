from dataclasses import dataclass
from importlib import import_module
from typing import Any, Callable, Optional

from agentforge.apis.base_api import NonRetriableModelError


@dataclass(frozen=True)
class CodexCredentials:
    account_id: str
    access_token: str


def _extract_value(payload: Any, *keys: str) -> Optional[str]:
    if payload is None:
        return None

    if isinstance(payload, dict):
        for key in keys:
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return None

    for key in keys:
        value = getattr(payload, key, None)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _normalize_credentials(payload: Any) -> Optional[CodexCredentials]:
    access_token = _extract_value(payload, "access_token", "access")
    account_id = _extract_value(payload, "account_id", "accountId")
    if not access_token or not account_id:
        return None
    return CodexCredentials(account_id=account_id, access_token=access_token)


def _load_oauth_helpers() -> tuple[Callable[[], Any], Callable[..., Any]]:
    try:
        oauth_module = import_module("oauth_cli_kit")
    except ImportError as exc:
        raise NonRetriableModelError(
            "Missing dependency `oauth-cli-kit`. Install it with `pip install oauth-cli-kit`."
        ) from exc

    get_token = getattr(oauth_module, "get_token", None)
    login_oauth_interactive = getattr(oauth_module, "login_oauth_interactive", None)
    if not callable(get_token) or not callable(login_oauth_interactive):
        raise NonRetriableModelError(
            "Installed `oauth-cli-kit` is missing required functions. Upgrade `oauth-cli-kit` and retry."
        )

    return get_token, login_oauth_interactive


def get_codex_credentials(
    interactive: bool = False,
    force_reauth: bool = False,
    print_fn=print,
    prompt_fn=input,
) -> CodexCredentials:
    get_token, login_oauth_interactive = _load_oauth_helpers()

    credentials = None
    if not force_reauth:
        credentials = _normalize_credentials(get_token())

    if credentials is None and interactive:
        print_fn("Starting Codex OAuth login...")
        try:
            login_oauth_interactive(print_fn=print_fn, prompt_fn=prompt_fn)
        except TypeError:
            login_oauth_interactive()
        credentials = _normalize_credentials(get_token())

    if credentials is None:
        raise NonRetriableModelError(
            "No Codex OAuth credentials found. Run `python -m agentforge.init_codex_oauth` to authenticate."
        )

    return credentials
