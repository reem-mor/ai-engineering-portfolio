"""Reset Open WebUI auth password inside a running Docker container."""

from __future__ import annotations

import argparse
import subprocess
import sys

DEFAULT_CONTAINER = "hw07-open-webui"
DEFAULT_EMAIL = "admin@localhost.com"
DEFAULT_PASSWORD = "admin"


def _bcrypt_hash(password: str) -> str:
    import bcrypt

    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def reset_auth(container: str, email: str, password: str, name: str) -> None:
    password_hash = _bcrypt_hash(password)
    code = (
        "import sqlite3\n"
        "conn = sqlite3.connect('/app/backend/data/webui.db')\n"
        "cur = conn.cursor()\n"
        f"cur.execute('UPDATE auth SET email=?, password=?, active=1', ({email!r}, {password_hash!r}))\n"
        f"cur.execute('UPDATE user SET email=?, name=?', ({email!r}, {name!r}))\n"
        "conn.commit()\n"
        "conn.close()\n"
        "print('ok')\n"
    )
    result = subprocess.run(
        ["docker", "exec", container, "python", "-c", code],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())


def main() -> int:
    parser = argparse.ArgumentParser(description="Reset Open WebUI password via Docker container")
    parser.add_argument("--container", default=DEFAULT_CONTAINER)
    parser.add_argument("--email", default=DEFAULT_EMAIL)
    parser.add_argument("--password", default=DEFAULT_PASSWORD)
    parser.add_argument("--name", default="Re'em Mor")
    args = parser.parse_args()
    try:
        reset_auth(args.container, args.email, args.password, args.name)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"OK: reset {args.email} on container {args.container}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
