"""Reset Open WebUI auth password for hw07 E2E (preserves KB and chats).

Uses Open WebUI's own password hasher inside the running container so sign-in
matches what the API expects. Normalizes email to admin@localhost.com by default.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import os

DEFAULT_CONTAINER = "hw07-open-webui"
DEFAULT_EMAIL = "admin@localhost.com"
DEFAULT_PASSWORD = "admin"
_HASH_RE = re.compile(r"^\$2[aby]\$")


def _run_container_python(container: str, code: str) -> str:
    result = subprocess.run(
        ["docker", "exec", container, "python", "-c", code],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    for line in reversed(result.stdout.splitlines()):
        line = line.strip()
        if _HASH_RE.match(line):
            return line
        if line.isdigit():
            return line
    raise RuntimeError(f"Unexpected container output:\n{result.stdout}")


def generate_password_hash(container: str, password: str) -> str:
    code = (
        "import asyncio\n"
        "from open_webui.utils.auth import get_password_hash\n"
        f"print(asyncio.run(get_password_hash({password!r})))"
    )
    return _run_container_python(container, code)


def reset_auth(container: str, email: str, password: str) -> int:
    password_hash = generate_password_hash(container, password)
    code = (
        "import sqlite3\n"
        "conn = sqlite3.connect('/app/backend/data/webui.db')\n"
        "cur = conn.cursor()\n"
        f"cur.execute('UPDATE auth SET email=?, password=?, active=1', ({email!r}, {password_hash!r}))\n"
        f"cur.execute('UPDATE user SET email=?, name=?', ({email!r}, 'HW07 Admin'))\n"
        "conn.commit()\n"
        "print(cur.rowcount)\n"
        "conn.close()\n"
    )
    updated = int(_run_container_python(container, code))
    if os.environ.get("HW07_SKIP_SIGNIN_VERIFY", "").strip().lower() in {"1", "true", "yes"}:
        return updated
    verify_code = (
        "import httpx\n"
        f"r = httpx.post('http://127.0.0.1:8080/api/v1/auths/signin', json={{'email': {email!r}, 'password': {password!r}}}, timeout=30.0)\n"
        "print(r.status_code)\n"
    )
    status = int(_run_container_python(container, verify_code))
    if status != 200:
        raise RuntimeError(f"Sign-in verification failed with HTTP {status}")
    return updated


def main() -> int:
    parser = argparse.ArgumentParser(description="Reset Open WebUI password via hw07 container")
    parser.add_argument("--container", default=DEFAULT_CONTAINER)
    parser.add_argument("--email", default=DEFAULT_EMAIL)
    parser.add_argument("--password", default=DEFAULT_PASSWORD)
    args = parser.parse_args()

    try:
        updated = reset_auth(args.container, args.email, args.password)
    except (RuntimeError, ValueError, subprocess.SubprocessError) as exc:
        print(f"Password reset failed: {exc}", file=sys.stderr)
        return 1

    print(f"Updated {updated} auth row(s) in {args.container}")
    print(f"Sign in: {args.email} / {args.password!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
