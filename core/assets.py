"""Helpers for resolving asset paths in development and bundled builds."""

from pathlib import Path
import sys


def _base_dir() -> Path:
    """Return the app base directory (supports PyInstaller)."""
    if hasattr(sys, "_MEIPASS"):
        return Path(getattr(sys, "_MEIPASS"))
    return Path(__file__).resolve().parent.parent


def asset_path(*parts: str) -> Path:
    return _base_dir().joinpath("assets", *parts)
