"""
One-time fix: move `backend/backend/*` up into `backend/` so the Python root is:

  .../projects/incident-assistant-rag/backend

Run from that directory:

  python flatten_layout.py

Safe to re-run: exits if the inner `backend` folder is already gone.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parent
    inner = root / "backend"
    if not inner.is_dir():
        print("Layout already flat (no nested backend/ folder). Nothing to do.")
        return 0

    for name in ("app", "tests"):
        if (root / name).exists():
            print(
                f"ERROR: {root / name} already exists. Remove or merge manually, then retry.",
                file=sys.stderr,
            )
            return 1

    items = list(inner.iterdir())
    if not items:
        inner.rmdir()
        print("Removed empty nested backend/ folder.")
        return 0

    for src in items:
        dest = root / src.name
        if dest.exists():
            alt = root / f"{src.name}.nested-archive"
            if alt.exists():
                print(
                    f"ERROR: conflict for {dest.name}: both exist and nested-archive name is taken.",
                    file=sys.stderr,
                )
                return 1
            dest = alt
            print(f"note: {src.name} already at root → saving nested copy as {dest.name}")
        print(f"move {src.relative_to(inner)} -> {dest}")
        shutil.move(str(src), str(dest))

    inner.rmdir()
    print("Done. Use this folder as cwd for uvicorn and pytest.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
