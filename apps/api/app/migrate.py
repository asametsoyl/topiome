"""Alembic entry point for the Topiome API.

Use this instead of the bare ``alembic`` command:

    uv run python -m app.migrate upgrade head
    uv run python -m app.migrate revision --autogenerate -m "add thing"

The repo lives on an exFAT disk where macOS writes ``._<name>.py`` AppleDouble
files next to every migration. Stock Alembic treats them as revisions and
crashes on their binary content, so revision discovery is patched to skip them.
"""

from __future__ import annotations

import re
import sys

from alembic.script import base as _script_base

from .config import API_DIR

ALEMBIC_INI = API_DIR / "alembic.ini"


def patch_alembic() -> None:
    _script_base._only_source_rev_file = re.compile(r"(?!\.\#|__init__|\._)(.*\.py)$")


def main(argv: list[str] | None = None) -> None:
    from alembic.config import main as alembic_main

    patch_alembic()
    alembic_main(argv=["-c", str(ALEMBIC_INI), *(argv if argv is not None else sys.argv[1:])])


if __name__ == "__main__":
    main()
