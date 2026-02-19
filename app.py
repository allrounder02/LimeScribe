"""Desktop entry point for the ZestVoice GUI runtime."""

from ui.app_runtime import run_gui_app


def main() -> int:
    return run_gui_app()


if __name__ == "__main__":
    raise SystemExit(main())
