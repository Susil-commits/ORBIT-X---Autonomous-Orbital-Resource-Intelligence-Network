"""CLI Wrapper to run the Formal Context Evaluation & Governance Harness from workspace root."""

import sys
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"

if __name__ == "__main__":
    script_path = BACKEND_DIR / "eval" / "run_context_eval.py"
    cmd = [sys.executable, str(script_path)]
    print(f"Executing: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(BACKEND_DIR))
    sys.exit(result.returncode)
