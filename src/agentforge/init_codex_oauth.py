import argparse
import sys

from agentforge.auth import get_codex_credentials


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Initialize or verify Codex OAuth credentials.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify that cached credentials already exist without launching interactive login.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force interactive OAuth login even when cached credentials exist.",
    )
    return parser


def main(argv=None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.check and args.force:
        parser.error("--check and --force cannot be used together.")

    interactive = not args.check
    force_reauth = bool(args.force)

    try:
        credentials = get_codex_credentials(
            interactive=interactive,
            force_reauth=force_reauth,
        )
        print(f"Codex OAuth ready. Account ID: {credentials.account_id}")
        return 0
    except KeyboardInterrupt:
        print("Codex OAuth setup cancelled by user.")
        return 1
    except Exception as exc:
        print(f"Codex OAuth setup failed: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
