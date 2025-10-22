import argparse
from typing import Optional, Sequence

from agent.runner.cli.update import build_update_subparser
from agent.project.cli.addproject import build_addproject_subparser
import os

ROLE = os.environ.get('ROLE', 'agent').lower()

# List of functions that build subparsers for different commands
AGENT_SUBPARSERS = [
    build_update_subparser,
    build_addproject_subparser,
]


def build_agent_parser():
    parser = argparse.ArgumentParser(description="Run the main application.")

    # Optional argument
    parser.add_argument("--dry-run",
                        action="store_true",
                        help="Perform a dry run without executing the main logic.")
    parser.add_argument("-v", "--verbose",
                        action="store_true",
                        help="Enable verbose output.")
    sub = parser.add_subparsers(dest="command", required=True)

    for build_subparser in AGENT_SUBPARSERS:
        build_subparser(sub)

    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_agent_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    import django

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'robo_atualizador.settings.{ROLE}')
    django.setup()

    raise SystemExit(main())
