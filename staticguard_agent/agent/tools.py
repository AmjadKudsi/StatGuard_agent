from typing import Dict, Any


def run_bandit_stub(path: str) -> Dict[str, Any]:
    """
    Temporary stub for the Bandit tool.

    Step 0: just pretend we scanned the path and found no issues.
    Step 1: this will run Bandit in JSON mode via subprocess.
    """
    return {
        "repo_path": path,
        "summary": {
            "HIGH": 0,
            "MEDIUM": 0,
            "LOW": 0,
        },
        "results": [],
    }
