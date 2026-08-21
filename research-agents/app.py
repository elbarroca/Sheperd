from __future__ import annotations

import sys
from pathlib import Path

source_root = str(Path(__file__).resolve().parent / "src")
if source_root not in sys.path:
    sys.path.insert(0, source_root)

from src.app import app  # noqa: E402

__all__ = ["app"]
