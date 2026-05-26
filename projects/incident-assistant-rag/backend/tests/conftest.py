"""Bootstrap path + load local secrets before importing the app."""

import os
import sys
from pathlib import Path


def _load_dotenv(path: Path) -> None:
    """Parse KEY=value from .env (no deps). Vars already in ``os.environ`` are not overwritten."""
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = val


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

_load_dotenv(BACKEND_ROOT / ".env")

# Last resort only (no .env / no OPENAI_* in shell) so collectors and constructors do not choke.
os.environ.setdefault("OPENAI_API_KEY", "sk-test-placeholder-not-used-for-network-calls")
os.environ.setdefault("SUPABASE_URL", "")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "")
