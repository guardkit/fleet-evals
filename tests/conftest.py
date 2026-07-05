"""Make the repo root importable so tests/ modules can `from harness import ...`.

Additive (FEAT-EVAL-IDEA, TASK-EVI-002): the frozen test_verifier_integrity.py
does not import harness and is unaffected; per-task test/ dirs keep their own
conftest pattern (po-held-004 precedent).
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
