#!/usr/bin/env python3
"""Headless ZestVoice CLI entry point."""

from core.cli_runtime import run_cli


def main() -> int:
    return run_cli()


if __name__ == "__main__":
    raise SystemExit(main())
