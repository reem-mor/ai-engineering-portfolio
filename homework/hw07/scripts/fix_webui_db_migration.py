"""Fix Open WebUI 0.6.x -> 0.10.x user.settings stored as legacy text JSON."""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path


def main() -> int:
    db_path = Path(sys.argv[1] if len(sys.argv) > 1 else "/data/webui.db")
    if not db_path.is_file():
        print(f"Database not found: {db_path}", file=sys.stderr)
        return 1

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM user")
    total = cur.fetchone()[0]
    # v0.10 expects deserialized JSON; NULL lets Open WebUI recreate defaults.
    cur.execute("UPDATE user SET settings = NULL")
    updated = cur.rowcount
    conn.commit()
    conn.close()
    print(f"Reset settings for {updated}/{total} users.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
